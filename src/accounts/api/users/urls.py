from django.conf.urls import url

from .views import (
    UserDetailAPIView,
    UserFoundedProjectAPIView,
    UserContributedProjectAPIView,
    UserOwnContributedProjectAPIView,
)


urlpatterns = [
    url(r'^(?P<id>\d+)/$', UserDetailAPIView.as_view(), name='detail'),
    url(r'^(?P<id>\d+)/founded_projects/$', UserFoundedProjectAPIView.as_view(),
        name='founded-projects-list'),
    url(r'^(?P<id>\d+)/contributed_projects/$', UserContributedProjectAPIView.as_view(),
        name='contributed-projects-list'),
    url(r'^contributed_projects/$', UserOwnContributedProjectAPIView.as_view(),
        name='own-contributed-projects-list')
]
