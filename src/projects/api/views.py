from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import generics, mixins, permissions, status

from utils.api import APIView
from projects.models import Project
from .serializers import (
    ProjectSerializer,
    ProjectInlineUserSerializer,
    ProjectInlineVerifySerializer,
    ProjectTargetSerializer,
    ProjectReleaseSerializer,
)
from tasks.api.serializers import TaskSerializer
from accounts.api.permissions import IsOwnerOrReadOnly, IsStaff
from accounts.api.users.serializers import UserInlineSerializer, EditContributorsSerializer


User = get_user_model()


class ProjectAPIView(mixins.CreateModelMixin, generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = ProjectSerializer

    passed_id = None
    search_fields = ('project_type', 'founder__email')
    ordering_fields = ('project_type', 'timestamp')
    filter_fields = ('project_type',)

    def get_queryset(self, *args, **kwargs):
        project_id = [x.id for x in Project.objects.filter(private=False) if x.project_status == 'in progress']
        projects = Project.objects.filter(pk__in=project_id)
        return projects

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(founder=self.request.user)


class ProjectAPIDetailView(mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = ProjectInlineUserSerializer
    queryset = Project.objects.all()
    lookup_field = 'id'

    def validate_status(self):
        project_id = self.kwargs.get("id", None)
        project = Project.objects.get(id=project_id)
        if project.verify_status in ['unreleased', 'verification failed']:
            return True

    def put(self, request, *args, **kwargs):
        if self.validate_status():
            return self.update(request, *args, **kwargs)
        else:
            return Response({"detail": "Not allowed here"}, status=400)

    def patch(self, request, *args, **kwargs):
        if self.validate_status():
            return self.update(request, *args, **kwargs)
        else:
            return Response({"detail": "Not allowed here"}, status=400)

    def delete(self, request, *args, **kwargs):
        if self.validate_status():
            return self.destroy(request, *args, **kwargs)
        else:
            return Response({"detail": "Not allowed here"}, status=400)


class ProjectReleaseView(generics.RetrieveAPIView, mixins.UpdateModelMixin):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = ProjectReleaseSerializer
    queryset = Project.objects.all()
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        project = Project.objects.get(id=project_id)
        if project.verify_status in ['unreleased', 'verification failed']:
            project.verify_status = 'verifying'
            project.save()
            return self.get(self, request, *args, **kwargs)
        else:
            return Response({"detail": "Not allowed here"}, status=400)


class ContributorsListView(generics.ListAPIView, mixins.UpdateModelMixin):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = UserInlineSerializer

    search_fields = ('email', 'full_name')
    ordering_fields = ('email', 'full_name')

    def get_queryset(self, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        if project_id is None:
            return User.objects.none()
        project = Project.objects.get(id=project_id)
        return project.contributors.all()

    def put(self, request, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        project = Project.objects.get(id=project_id)
        user = request.user
        if user in project.contributors.all():
            project.contributors.remove(user)
            return Response({"message": "You have successfully exited the project!"}, status=200)
        else:
            project.contributors.add(user)
            return Response({"message": "You have successfully entered the project!"}, status=200)


class ProjectEditContributorsView(generics.ListAPIView, mixins.UpdateModelMixin):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = EditContributorsSerializer

    search_fields = ('email', 'full_name')
    ordering_fields = ('email', 'full_name')

    def get_queryset(self, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        if project_id is None:
            return User.objects.none()
        project = Project.objects.get(id=project_id)
        return project.contributors.all()

    def put(self, request, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        project = Project.objects.get(id=project_id)
        user_id = request.data.get("id")
        user = get_object_or_404(User, id=user_id)
        if user is None:
            return Response({"message": "User does not exist"}, status=400)
        if user in project.contributors.all():
            project.contributors.remove(user)
            return Response({"message": "User has successfully exited the project!"}, status=200)
        else:
            project.contributors.add(user)
            return Response({"message": "User has successfully entered the project!"}, status=200)


class ProjectVerifyListView(generics.ListAPIView):
    Permission_classes = [IsStaff]
    serializer_class = ProjectSerializer

    search_fields = ('project_type', 'founder__email')
    ordering_fields = ('project_type', 'timestamp')
    queryset = Project.objects.filter(verify_status='verifying')


class ProjectVerifyDetailView(generics.RetrieveAPIView, mixins.UpdateModelMixin):
    Permission_classes = [IsStaff]
    serializer_class = ProjectInlineVerifySerializer

    def get_object(self, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        project = get_object_or_404(Project, id=project_id)
        return project

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if instance.verify_status == 'verifying':
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)
        elif instance:
            return Response({"message": "Verification is not allowed"}, status=400)
        else:
            return Response({"message": "Project not exists"}, status=400)

    def perform_update(self, serializer):
        serializer.save(verify_staff=self.request.user)


class ProjectTargetDetailView(generics.RetrieveAPIView, mixins.UpdateModelMixin):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = ProjectTargetSerializer
    queryset = Project.objects.all()
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class ProjectResultView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = TaskSerializer

    search_fields = ('contributor', 'label')
    ordering_fields = ('contributor', 'updated')

    def get_queryset(self, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        project = get_object_or_404(Project, id=project_id)
        return project.task_set.all().exclude(label='')
