from django.conf.urls import url

from .views import (
    OrdinaryUserAPIView,
    UserTypeAPIView,
    UserDetailAPIView,
    UserFoundedProjectAPIView,
    UserOwnFoundedProjectAPIView,
    UserContributedProjectAPIView,
    UserOwnContributedProjectAPIView,
    UserInspectedProjectAPIView,
    UserOwnInspectedProjectAPIView,
    UserUpdateInfoAPIView,
    UserPasswordAPIView,
)


urlpatterns = [
    url(r'^$', OrdinaryUserAPIView.as_view(), name='ordinary-users-list'),
    url(r'^type$', UserTypeAPIView.as_view(), name='user-type'),
    url(r'^(?P<id>\d+)/$', UserDetailAPIView.as_view(), name='detail'),
    url(r'^(?P<id>\d+)/founded_projects/$', UserFoundedProjectAPIView.as_view(),
        name='founded-projects-list'),
    url(r'^founded_projects/$', UserOwnFoundedProjectAPIView.as_view(),
        name='my-founded-projects-list'),
    url(r'^(?P<id>\d+)/contributed_projects/$', UserContributedProjectAPIView.as_view(),
        name='contributed-projects-list'),
    url(r'^contributed_projects/$', UserOwnContributedProjectAPIView.as_view(),
        name='my-contributed-projects-list'),
    url(r'^(?P<id>\d+)/inspected_projects/$', UserInspectedProjectAPIView.as_view(),
        name='inspected-projects-list'),
    url(r'^inspected_projects/$', UserOwnInspectedProjectAPIView.as_view(),
        name='my-inspected-projects-list'),
    url(r'^info/$', UserUpdateInfoAPIView.as_view(), name='my-info'),
    url(r'^update_password/$', UserPasswordAPIView.as_view(), name='my-password'),
]
