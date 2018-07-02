from django.conf.urls import url

from .views import (
    OrdinaryUserAPIView,
    UserDetailAPIView,
    UserFoundedProjectAPIView,
    UserContributedProjectAPIView,
    UserOwnContributedProjectAPIView,
    UserPasswordAPIView,
)


urlpatterns = [
    url(r'^$', OrdinaryUserAPIView.as_view(), name='ordinary-users-list'),
    url(r'^(?P<id>\d+)/$', UserDetailAPIView.as_view(), name='detail'),
    url(r'^(?P<id>\d+)/founded_projects/$', UserFoundedProjectAPIView.as_view(),
        name='founded-projects-list'),
    url(r'^(?P<id>\d+)/contributed_projects/$', UserContributedProjectAPIView.as_view(),
        name='contributed-projects-list'),
    url(r'^contributed_projects/$', UserOwnContributedProjectAPIView.as_view(),
        name='own-contributed-projects-list'),
    url(r'^update_password/$', UserPasswordAPIView.as_view(), name='my-password'),
]
