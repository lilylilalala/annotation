from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import generics, mixins, permissions

from projects.models import Project
from tasks.models import Task
from .serializers import TaskSerializer
from accounts.api.permissions import IsContributorOrReadOnly


class TaskDetailView(generics.RetrieveAPIView, mixins.UpdateModelMixin):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsContributorOrReadOnly]
    serializer_class = TaskSerializer

    def get_object(self, *args, **kwargs):
        project_id = self.kwargs.get("id", None)
        project = get_object_or_404(Project, id=project_id)
        spare_set = Task.objects.filter(project=project_id, label='')
        if spare_set:
            return spare_set.first()
        return Task.objects.none().first()

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance:
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        return Response({"message": "Project Completed"}, status=200)

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
            return Response({"message": "Project Completed"}, status=200)

    def perform_update(self, serializer):
        serializer.save(contributor=self.request.user)
