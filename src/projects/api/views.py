from django.contrib.auth import get_user_model
from rest_framework import generics, mixins, permissions

from projects.models import Project
from .serializers import ProjectSerializer, ProjectInlineUserSerializer
from accounts.api.permissions import IsOwnerOrReadOnly
from accounts.api.users.serializers import UserInlineSerializer


User = get_user_model()


class ProjectAPIView(mixins.CreateModelMixin, generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = ProjectSerializer

    passed_id = None
    search_fields = ('project_type', 'founder_email')
    ordering_fields = ('project_type', 'timestamp')
    queryset = Project.objects.all()

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(founder=self.request.user)


class ProjectAPIDetailView(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    generics.RetrieveAPIView):
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


class ContributorsListView(mixins.UpdateModelMixin, generics.ListAPIView):
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
