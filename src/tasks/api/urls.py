from django.conf.urls import url

from .views import TaskContributeView, TaskInspectView, TaskContributeUpdateView


urlpatterns = [
    url(r'^(?P<id>\d+)/contribute/$', TaskContributeView.as_view(), name='contribute'),
    url(r'^(?P<id>\d+)/inspect/$', TaskInspectView.as_view(), name='inspect'),
    url(r'^update/(?P<id>\d+)/$', TaskContributeUpdateView.as_view(), name='update'),
]
