import random

from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import generics, mixins, permissions

from projects.models import Project
from tasks.models import Task
from quizzes.models import QuizContributor
from .serializers import TaskSerializer
from accounts.api.permissions import IsContributorOrReadOnly, HasContributed, IsInspectorOrReadOnly
import django.utils.timezone as timezone


class TaskDetailView(generics.RetrieveAPIView, mixins.UpdateModelMixin):
    """
    get:
        【标注任务】 随机获取任务中的一道该用户未解答的问题

    put:
        【标注任务】 答题，给问题添加目标标签

    patch:
        【标注任务】 答题，给问题添加目标标签
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsContributorOrReadOnly]
    serializer_class = TaskSerializer

    def get_object(self, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        user = self.request.user
        user_done_set = Task.objects.filter(project=project_id, contributor=user, type=0)
        copies = user_done_set.values_list("copy", flat=True)
        spare_set = Task.objects.filter(project=project_id, type=0, label='').exclude(copy__in=set(copies))
        if spare_set:
            ids = spare_set.values_list("id", flat=True)
            rand_id = random.sample(set(ids), 1)[0]
            return spare_set.get(id=rand_id)
        return Task.objects.none().first()

    def get(self, request, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        project = get_object_or_404(Project, id=project_id)
        if project.verify_status != 'verification succeed':
            return Response({"message": "Project is not verified yet."}, status=400)
        if project.quiz:
            user = request.user
            if user not in project.quiz.contributors.all():
                return Response({"message": "Please do the quiz first."}, status=400)
            qc = QuizContributor.objects.get(quiz=project.quiz, contributor=user)
            if not qc.is_completed:
                return Response({"message": "You have not finish the quiz yet."}, status=400)
            if qc.accuracy < project.accuracy_requirement:
                return Response({"message": "You have failed the quiz."}, status=400)
        instance = self.get_object()
        if instance:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response({"message": "Tasks Completed"}, status=200)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            if serializer.validated_data["label"]:
                if not instance.created:
                    serializer.validated_data["created"] = timezone.now()
                self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}
            return Response(serializer.data)
        else:
            return Response({"message": "Tasks Completed"}, status=200)

    def perform_update(self, serializer):
        serializer.save(contributor=self.request.user)


class TaskCheckView(generics.RetrieveAPIView, mixins.UpdateModelMixin):
    """
    get:
        【质检任务】 获取任务中需要检查的问题（仅限于分类任务）

    put:
        【质检任务】 答题，给问题添加目标标签

    patch:
        【质检任务】 答题，给问题添加目标标签
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsInspectorOrReadOnly]
    serializer_class = TaskSerializer

    def create_check_tasks(self, *args, **kwargs):
        return 1

    def get_object(self, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        spare_set = Task.objects.filter(project=project_id, type=1, label='')
        if spare_set:
            return spare_set.first()
        return Task.objects.none().first()

    def get(self, request, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        project = get_object_or_404(Project, id=project_id)
        if project.project_type not in ['DataClassification', 'TextClassification']:
            return Response({"message": "This is not a classification project."}, status=400)
        if project.repetition_rate == 1.0:
            return Response({"message": "No need to check since repetition_rate is 1.0."}, status=400)
        self.create_check_tasks()
        instance = self.get_object()
        if instance:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response({"message": "Check Completed"}, status=200)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            if serializer.validated_data["label"]:
                if not instance.created:
                    serializer.validated_data["created"] = timezone.now()
                self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}
            return Response(serializer.data)
        else:
            return Response({"message": "Check Completed"}, status=200)

    def perform_update(self, serializer):
        serializer.save(contributor=self.request.user)


class TaskUpdateView(generics.RetrieveUpdateAPIView):
    """
    get:
        【参与任务】 根据task id，获取已答过的题目详情

    put:
        【参与任务】 修改题目标签，非空

    patch:
        【参与任务】 修改题目标签，非空
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, HasContributed]
    serializer_class = TaskSerializer
    queryset = Task.objects.all()
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        if request.data['label']:
            return self.update(request, *args, **kwargs)
        else:
            return Response({"message": "Label should not be empty"}, status=400)

    def patch(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)
