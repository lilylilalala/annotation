from django.contrib.auth import get_user_model
from rest_framework import generics, mixins, permissions

from targets.models import Target
from .serializers import TargetSerializer
from accounts.api.permissions import IsOwnerOrReadOnly, IsStaff, IsOwner


User = get_user_model()


class TargetAPIView(mixins.CreateModelMixin, generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    serializer_class = TargetSerializer

    passed_id = None
    search_fields = ('name', 'type', )
    ordering_fields = ('updated', 'type')

    def get_queryset(self, *args, **kwargs):
        target_type = self.request.GET.get("type", None)
        return Target.objects.filter(user=self.request.user, type=target_type)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TargetAPIDetailView(mixins.UpdateModelMixin, mixins.DestroyModelMixin, generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    serializer_class = TargetSerializer
    queryset = Target.objects.all()
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
