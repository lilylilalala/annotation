from django.conf.urls import url

from .views import (
    TargetAPIView,
    TargetAPIDetailView,
    TargetTypeAPIView,
)


urlpatterns = [
    url(r'^$', TargetAPIView.as_view(), name='list'),
    url(r'^(?P<id>\d+)/$', TargetAPIDetailView.as_view(), name='detail'),
    url(r'^types/$', TargetTypeAPIView.as_view(), name='type_list'),
]
