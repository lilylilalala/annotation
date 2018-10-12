from django.contrib.auth import get_user_model, authenticate
from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from projects.models import Project
from projects.api.views import ProjectAPIView
from .serializers import UserDetailSerializer, UserInlineSerializer, UserDetailUpdateSerializer, UserPasswordUpdateSerializer
from projects.api.serializers import ProjectInlineUserSerializer
from accounts.api.permissions import IsOwnerOrReadOnly


User = get_user_model()


class OrdinaryUserAPIView(generics.ListAPIView):
    """
    get:
        【成员管理】 获取普通用户列表
    """
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = User.objects.filter(user_type='ordinary_user')

    search_fields = ('email', 'full_name')
    ordering_fields = ('email', 'full_name')


class UserTypeAPIView(generics.RetrieveAPIView):
    """
    get:
        获取当前用户类型
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserInlineSerializer
    queryset = User.objects.filter(is_active=True)

    def get_object(self, *args, **kwargs):
        return self.request.user


class UserDetailAPIView(generics.RetrieveAPIView):
    """
    get:
        【成员管理】 获取当前用户详情
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = UserDetailSerializer
    queryset = User.objects.filter(is_active=True)
    lookup_field = 'id'


class UserFoundedProjectAPIView(ProjectAPIView):
    """
    get:
        【任务管理】 获取用户创建的任务列表

    post:
        没有post方法
    """
    serializer_class = ProjectInlineUserSerializer

    def get_queryset(self, *args, **kwargs):
        user_id = self.kwargs.get("id", None)
        if user_id is None:
            return Project.objects.none()
        user = get_object_or_404(User, id=user_id)
        return user.founded_projects.all()

    def post(self, request, *args, **kwargs):
        return Response({"detail": "Not allowed here"}, status=400)


class UserOwnFoundedProjectAPIView(ProjectAPIView):
    """
    get:
        【任务管理】 根据用户id，获取当前用户创建的任务列表

    post:
        没有post方法
    """
    serializer_class = ProjectInlineUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    search_fields = ('name', 'project_type')
    ordering_fields = ('name', 'project_type', 'timestamp')
    filter_fields = ('project_type',)

    def get_queryset(self, *args, **kwargs):
        user_id = self.request.user.id
        if user_id is None:
            return Project.objects.none()
        user = User.objects.get(id=user_id)
        projects = user.founded_projects.all()
        project_status = self.request.GET.get("project_status", None)
        if project_status:
            project_id = [x.id for x in projects if x.project_status == project_status]
            return projects.filter(pk__in=project_id)
        return projects

    def post(self, request, *args, **kwargs):
        return Response({"detail": "Not allowed here"}, status=400)


class UserContributedProjectAPIView(UserFoundedProjectAPIView):
    """
    get:
        【参与任务】 根据用户id，获取用户参与的任务列表

    post:
        没有post方法
    """
    def get_queryset(self, *args, **kwargs):
        user_id = self.kwargs.get("id", None)
        if user_id is None:
            return Project.objects.none()
        user = get_object_or_404(User, id=user_id)
        return user.contributed_projects.all()


class UserOwnContributedProjectAPIView(ProjectAPIView):
    """
    get:
        【参与任务】 获取当前用户参与的任务列表

    post:
        没有post方法
    """
    serializer_class = ProjectInlineUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    search_fields = ('name', 'project_type')
    ordering_fields = ('name', 'project_type', 'timestamp')
    filter_fields = ('project_type', 'status')

    def get_queryset(self, *args, **kwargs):
        user_id = self.request.user.id
        if user_id is None:
            return Project.objects.none()
        user = User.objects.get(id=user_id)
        projects = user.contributed_projects.filter(status__in=['answering', 'checking', 'completed'])
        return projects

    def post(self, request, *args, **kwargs):
        return Response({"detail": "Not allowed here"}, status=400)


class UserInspectedProjectAPIView(UserFoundedProjectAPIView):
    """
    get:
        【参与任务】 根据用户id，获取用户检查的任务列表

    post:
        没有post方法
    """
    def get_queryset(self, *args, **kwargs):
        user_id = self.kwargs.get("id", None)
        if user_id is None:
            return Project.objects.none()
        user = get_object_or_404(User, id=user_id)
        return user.inspected_projects.all()


class UserOwnInspectedProjectAPIView(ProjectAPIView):
    """
    get:
        【参与任务】 获取当前用户检查的任务列表

    post:
        没有post方法
    """
    serializer_class = ProjectInlineUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    search_fields = ('name', 'project_type')
    ordering_fields = ('name', 'project_type', 'timestamp')
    filter_fields = ('project_type', 'status')

    def get_queryset(self, *args, **kwargs):
        user_id = self.request.user.id
        if user_id is None:
            return Project.objects.none()
        user = User.objects.get(id=user_id)
        projects = user.inspected_projects.filter(status__in=['answering', 'checking', 'completed'])
        return projects

    def post(self, request, *args, **kwargs):
        return Response({"detail": "Not allowed here"}, status=400)


class UserUpdateInfoAPIView(generics.RetrieveAPIView, mixins.UpdateModelMixin):
    """
    get:
        【个人中心】 获取我的信息

    put:
        【个人中心】 修改个人信息

    patch:
        【个人中心】 修改个人信息
    """
    serializer_class = UserDetailUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user_id = self.request.user.id
        if user_id is None:
            return User.objects.none()
        return User.objects.get(id=user_id)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class UserPasswordAPIView(generics.CreateAPIView):
    """
    post:
        【个人中心】 修改密码
    """
    serializer_class = UserPasswordUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}
