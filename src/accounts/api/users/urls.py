from django.conf.urls import url

from .views import (
    UserDetailAPIView,
    UserFoundedProjectAPIView,
    UserContributedProjectAPIView,
)


urlpatterns = [
    url(r'^(?P<id>\w+)/$', UserDetailAPIView.as_view(), name='detail'),
    url(r'^(?P<id>\w+)/founded_projects/$', UserFoundedProjectAPIView.as_view(),
        name='founded-projects-list'),
    url(r'^(?P<id>\w+)/contributed_projects/$', UserContributedProjectAPIView.as_view(),
        name='contributed-projects-list'),
]
