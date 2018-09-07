from django.conf.urls import url

from .views import TaskDetailView, TaskCheckView, TaskUpdateView


urlpatterns = [
    url(r'^(?P<id>\d+)/$', TaskDetailView.as_view(), name='detail'),
    url(r'^(?P<id>\d+)/check/$', TaskCheckView.as_view(), name='check'),
    url(r'^update/(?P<id>\d+)/$', TaskUpdateView.as_view(), name='update'),
]
