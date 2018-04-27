from django.contrib.auth import get_user_model
from rest_framework import generics, mixins
from rest_framework.response import Response

from projects.models import Project
from projects.api.views import ProjectAPIView
from .serializers import UserDetailSerializer, UserDetailUpdateSerializer
from projects.api.serializers import ProjectInlineUserSerializer
from accounts.api.permissions import IsOwnerOrReadOnly


User = get_user_model()


class UserDetailAPIView(generics.RetrieveAPIView, mixins.UpdateModelMixin):
    permission_classes = [IsOwnerOrReadOnly]
    queryset = User.objects.filter(is_active=True)
    lookup_field = 'id'

    def get_serializer_context(self):
        return {'request': self.request}

    def get_serializer_class(self, *args, **kwargs):
        if self.request.user == self.get_object():
            return UserDetailUpdateSerializer
        else:
            return UserDetailSerializer

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class UserFoundedProjectAPIView(ProjectAPIView):
    serializer_class = ProjectInlineUserSerializer

    def get_queryset(self, *args, **kwargs):
        user_id = self.kwargs.get("id", None)
        if user_id is None:
            return Project.objects.none()
        user = User.objects.get(id=user_id)
        return user.founded_projects.all()

    def post(self, request, *args, **kwargs):
        return Response({"detail": "Not allowed here"}, status=400)


class UserContributedProjectAPIView(UserFoundedProjectAPIView):
    def get_queryset(self, *args, **kwargs):
        user_id = self.kwargs.get("id", None)
        if user_id is None:
            return Project.objects.none()
        user = User.objects.get(id=user_id)
        return user.contributed_projects.all()
