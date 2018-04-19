from django.conf.urls import url

from .views import ProjectAPIView, ProjectAPIDetailView, ContributorsListView


urlpatterns = [
    url(r'^$', ProjectAPIView.as_view(), name='list'),
    url(r'^(?P<id>\d+)/$', ProjectAPIDetailView.as_view(), name='detail'),
    url(r'^contributors/(?P<id>\d+)/$', ContributorsListView.as_view(), name='contributors'),
]