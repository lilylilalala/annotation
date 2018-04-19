from django.conf.urls import url

from .views import TaskDetailView


urlpatterns = [
    url(r'^(?P<id>\d+)/$', TaskDetailView.as_view(), name='detail'),
]
