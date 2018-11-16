from rest_framework.response import Response
from rest_framework import generics, mixins, permissions
from django.shortcuts import get_object_or_404

from tags.models import Tag


from .serializers import (
    TagSerializer,
    TagDetailSerializer,
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

    search_fields = ('name', 'founder')
    ordering_fields = ('name', 'updated')
    filter_fields = ('level',)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(founder=self.request.user)


class TagAPIDetailView(mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.RetrieveAPIView):
    """
    get:
        【任务管理】 获取标签详情

    put:
        【目标管理】 编辑标签(只编辑名称和描述,用过的标签不能编辑)

    delete:
        【目标管理】 删除标签(用过的标签不能删除)
    """
    permission_classes = [IsAdmin]
    serializer_class = TagDetailSerializer
    queryset = Tag.objects.all()
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        tag_id = self.kwargs.get("id", None)
        tag = get_object_or_404(Tag, id=tag_id)
        if not tag.editable:
            return Response({"message": "The tag is already in use and cannot be updated!"}, status=400)
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        tag_id = self.kwargs.get("id", None)
        tag = get_object_or_404(Tag, id=tag_id)
        if not tag.deletable:
            return Response({"message": "The tag is already in use or has child tags cannot be deleted!"}, status=400)
        return self.destroy(request, *args, **kwargs)
