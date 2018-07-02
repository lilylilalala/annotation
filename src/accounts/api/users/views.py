from django.contrib.auth import get_user_model, authenticate
from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response

from projects.models import Project
from projects.api.views import ProjectAPIView
from .serializers import UserDetailSerializer, UserDetailUpdateSerializer, UserPasswordUpdateSerializer
from projects.api.serializers import ProjectInlineUserSerializer
from accounts.api.permissions import IsOwnerOrReadOnly


User = get_user_model()


class OrdinaryUserAPIView(generics.ListAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = User.objects.filter(user_type='ordinary_user')

    search_fields = ('email', 'full_name')
    ordering_fields = ('email', 'full_name')


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


class UserOwnContributedProjectAPIView(ProjectAPIView):
    serializer_class = ProjectInlineUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        user_id = self.request.user.id
        if user_id is None:
            return Project.objects.none()
        user = User.objects.get(id=user_id)
        return user.contributed_projects.all()

    def post(self, request, *args, **kwargs):
        return Response({"detail": "Not allowed here"}, status=400)


class UserPasswordAPIView(generics.CreateAPIView):
    serializer_class = UserPasswordUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}