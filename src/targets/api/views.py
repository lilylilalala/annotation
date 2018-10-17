from django.contrib.auth import get_user_model
from rest_framework import generics, mixins, permissions

from targets.models import Target, TargetType
from .serializers import TargetSerializer, TargetTypeSerializer
from accounts.api.permissions import IsOwnerOrReadOnly, IsStaff


User = get_user_model()


class TargetAPIView(mixins.CreateModelMixin, generics.ListAPIView):
    """
    get:
        【目标管理】 获取发起人创建的目标列表

    post:
        【目标管理】 新增目标
    """
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = TargetSerializer

    passed_id = None
    search_fields = ('name', )
    ordering_fields = ('updated', 'type')
    filter_fields = ('type',)

    def get_queryset(self, *args, **kwargs):
        return Target.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TargetAPIDetailView(mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.RetrieveAPIView):
    """
    get:
        【目标管理】 获取目标详情（仅发起人可见）

    put:
        【目标管理】 编辑目标

    patch:
        【目标管理】 编辑目标

    delete:
        【目标管理】 删除目标

    """
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = TargetSerializer
    lookup_field = 'id'

    def get_queryset(self, *args, **kwargs):
        return Target.objects.filter(user=self.request.user)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class TargetTypeAPIView(generics.ListAPIView):
    """
    get:
        【目标管理】 获取目标类型列表
    """
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = TargetTypeSerializer
    queryset = TargetType.objects.all()
