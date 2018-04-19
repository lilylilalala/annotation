from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.response import Response

from projects.models import Project
from projects.api.views import ProjectAPIView
from .serializers import UserDetailSerializer
from projects.api.serializers import ProjectInlineUserSerializer

User = get_user_model()


class UserDetailAPIView(generics.RetrieveAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserDetailSerializer
    lookup_field = 'username'

    def get_serializer_context(self):
        return {'request': self.request}


class UserFoundedProjectAPIView(ProjectAPIView):
    serializer_class = ProjectInlineUserSerializer

    def get_queryset(self, *args, **kwargs):
        username = self.kwargs.get("username", None)
        if username is None:
            return Project.objects.none()
        user = User.objects.get(username=username)
        return user.founded_projects.all()

    def post(self, request, *args, **kwargs):
        return Response({"detail": "Not allowed here"}, status=400)


class UserContributedProjectAPIView(UserFoundedProjectAPIView):
    def get_queryset(self, *args, **kwargs):
        username = self.kwargs.get("username", None)
        if username is None:
            return Project.objects.none()
        user = User.objects.get(username=username)
        return user.contributed_projects.all()
