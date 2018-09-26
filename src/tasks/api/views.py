import random

from django.shortcuts import get_object_or_404
import django.utils.timezone as timezone

from rest_framework.response import Response
from rest_framework import generics, mixins, permissions

from projects.models import Project
from tasks.models import Task, Contribution, Inspection
from quizzes.models import QuizContributor
from .serializers import TaskContributeSerializer, TaskInspectSerializer, TaskContributeUpdateSerializer
from accounts.api.permissions import IsContributorOrReadOnly, HasContributed, IsInspectorOrReadOnly


class TaskContributeView(generics.RetrieveAPIView, mixins.UpdateModelMixin):
    """
    get:
        【标注任务】 随机获取任务中的一道该用户未解答的问题

    put:
        【标注任务】 答题，给问题添加目标标签

    patch:
        【标注任务】 答题，给问题添加目标标签
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsContributorOrReadOnly]
    serializer_class = TaskContributeSerializer

    def get_object(self, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        user = self.request.user
        user_con_set = Contribution.objects.filter(project=project_id, contributor=user)
        tasks = user_con_set.values_list('task', flat=True)
        spare_set = Contribution.objects.filter(project=project_id, label='').exclude(task__in=tasks)
        if spare_set:
            ids = spare_set.values_list('id', flat=True)
            rand_id = random.sample(list(ids), 1)[0]
            return spare_set.get(id=rand_id)
        return Contribution.objects.none().first()

    def get(self, request, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        project = get_object_or_404(Project, id=project_id)
        if project.verify_status != 'passed':
            return Response({"message": "Project hasn't passed the verification yet."}, status=400)
        if project.quiz:
            user = request.user
            if user not in project.quiz.contributors.all():
                return Response({"message": "Please do the quiz first."}, status=400)
            qc = QuizContributor.objects.get(quiz=project.quiz, contributor=user)
            if not qc.is_completed:
                return Response({"message": "You have not finished the quiz yet."}, status=400)
            if qc.accuracy < project.accuracy_requirement:
                return Response({"message": "You have failed the quiz."}, status=400)
        instance = self.get_object()
        if instance:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response({"message": "Contribution Completed"}, status=200)

    def put(self, request, *args, **kwargs):
        if request.data['label']:
            contribution_id = request.data.get("contribution_id")
            instance = get_object_or_404(Contribution, id=contribution_id)
            instance.label = request.data['label']
            instance.contributor = request.user
            try:
                if request.data['submitted'] == 'true':
                    instance.submitted = True
            except:
                pass
            if not instance.created:
                instance.created = timezone.now()
            instance.save()
        return self.get(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)


class TaskInspectView(generics.RetrieveAPIView, mixins.UpdateModelMixin):
    """
    get:
        【质检任务】 获取任务中需要检查的问题（仅限于分类任务）

    put:
        【质检任务】 答题，给问题添加目标标签

    patch:
        【质检任务】 答题，给问题添加目标标签
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsInspectorOrReadOnly]
    serializer_class = TaskInspectSerializer

    def get_object(self, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        spare_set = Inspection.objects.filter(project=project_id, label='')
        if spare_set:
            return spare_set.first()
        return Task.objects.none().first()

    def get(self, request, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        project = get_object_or_404(Project, id=project_id)
        if project.project_status == 'completed':
            return Response({"message": "Project Completed."}, status=200)
        elif project.project_status != 'checking':
            return Response({"message": "Not allowed to check."}, status=400)
        else:
            instance = self.get_object()
            if instance:
                serializer = self.get_serializer(instance)
                return Response(serializer.data)
            return Response({"message": "Inspection Completed"}, status=200)

    def put(self, request, *args, **kwargs):
        if request.data['label']:
            instance = self.get_object()
            instance.label = request.data['label']
            instance.inspector = request.user
            try:
                if request.data['submitted'] == 'true':
                    instance.submitted = True
            except:
                pass
            if not instance.created:
                instance.created = timezone.now()
            instance.save()
        return self.get(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)


class TaskContributeUpdateView(generics.RetrieveUpdateAPIView):
    """
    get:
        【参与任务】 根据task id，获取已答过的题目详情

    put:
        【参与任务】 修改题目标签，非空

    patch:
        【参与任务】 修改题目标签，非空
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, HasContributed]
    serializer_class = TaskContributeUpdateSerializer
    queryset = Contribution.objects.all()
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        if request.data['label']:
            return self.update(request, *args, **kwargs)
        else:
            return Response({"message": "Label should not be empty"}, status=400)

    def patch(self, request, *args, **kwargs):
        return self.put(request, *args, **kwargs)
