from django.conf.urls import url

from .views import (
    TagAPIView,
    TagAPIDetailView,
)


urlpatterns = [
    url(r'^$', TagAPIView.as_view(), name='list'),
    url(r'^(?P<id>\d+)/$', TagAPIDetailView.as_view(), name='detail'),
]
