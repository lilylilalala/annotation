from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import generics, mixins, permissions

from projects.models import Project
from .serializers import ProjectSerializer, ProjectInlineUserSerializer, ProjectInlineVerifySerializer
from accounts.api.permissions import IsOwnerOrReadOnly, IsStaff
from accounts.api.users.serializers import UserInlineSerializer


User = get_user_model()


class ProjectAPIView(mixins.CreateModelMixin, generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = ProjectSerializer

    passed_id = None
    search_fields = ('project_type', 'founder__email')
    ordering_fields = ('project_type', 'timestamp')
    queryset = Project.objects.filter(private=False, verify_status='verification succeed')

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(founder=self.request.user)


class ProjectAPIDetailView(mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = ProjectInlineUserSerializer
    queryset = Project.objects.all()
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ContributorsListView(generics.ListAPIView, mixins.UpdateModelMixin, ):
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
        else:
            project.contributors.add(user)


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
        if instance:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            return Response(serializer.data)
        else:
            return Response({"message": "Project not exists"}, status=400)

    def perform_update(self, serializer):
        serializer.save(verify_staff=self.request.user)
