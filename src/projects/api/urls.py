from django.conf.urls import url

from .views import (
    ProjectAPIView,
    ProjectAPIDetailView,
    ContributorsListView,
    ProjectVerifyListView,
    ProjectVerifyDetailView,
    ProjectTargetDetailView,
    ProjectResultView,
)


urlpatterns = [
    url(r'^$', ProjectAPIView.as_view(), name='list'),
    url(r'^(?P<id>\d+)/$', ProjectAPIDetailView.as_view(), name='detail'),
    url(r'^(?P<id>\d+)/target$', ProjectTargetDetailView.as_view(), name='target'),
    url(r'^(?P<id>\d+)/result', ProjectResultView.as_view(), name='result'),
    url(r'^(?P<id>\d+)/contributors/$', ContributorsListView.as_view(), name='contributors'),
    url(r'^verify/$', ProjectVerifyListView.as_view(), name='verify-projects-list'),
    url(r'^(?P<id>\d+)/verify/$', ProjectVerifyDetailView.as_view(), name='verify-projects-detail')
]