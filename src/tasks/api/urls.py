from django.conf.urls import url

from .views import TaskContributeView, TaskInspectView, TaskContributeUpdateView, TaskInspectUpdateView


urlpatterns = [
    url(r'^(?P<id>\d+)/contribute/$', TaskContributeView.as_view(), name='contribute'),
    url(r'^(?P<id>\d+)/inspect/$', TaskInspectView.as_view(), name='inspect'),
    url(r'^update/(?P<id>\d+)/$', TaskContributeUpdateView.as_view(), name='contribution_update'),
    url(r'^inspection_update/(?P<id>\d+)/$', TaskInspectUpdateView.as_view(), name='inspection_update'),
]
