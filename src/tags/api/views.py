from rest_framework.response import Response
from rest_framework import generics, mixins, permissions

from tags.models import Tag
from .serializers import (
    TagSerializer,
)
from accounts.api.permissions import IsAdmin


class TagAPIView(mixins.CreateModelMixin, generics.ListAPIView):
    """
    get:
        【任务管理】 获取所有标签

    post:
        【任务管理】 新建标签
    """
    permission_classes = [IsAdmin]
    serializer_class = TagSerializer
    queryset = Tag.objects.all()

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(founder=self.request.user)