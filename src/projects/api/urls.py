from django.conf.urls import url

from .views import (
    ProjectAPIView,
    ProjectAPIDetailView,
    ProjectReleaseView,
    ContributorsListView,
    ProjectAddContributorsView,
    ProjectDeleteContributorsView,
    ProjectVerifyListView,
    ProjectVerifyDetailView,
    ProjectTargetDetailView,
    ProjectResultView,
    ProjectMyContributionView,
    ProjectMyInspectionView,
    ProjectResultDownloadView,
)


urlpatterns = [
    url(r'^$', ProjectAPIView.as_view(), name='list'),
    url(r'^(?P<id>\d+)/$', ProjectAPIDetailView.as_view(), name='detail'),
    url(r'^(?P<id>\d+)/target/$', ProjectTargetDetailView.as_view(), name='target'),
    url(r'^(?P<id>\d+)/release/$', ProjectReleaseView.as_view(), name='release'),
    url(r'^(?P<id>\d+)/contributors/$', ContributorsListView.as_view(), name='contributors'),
    url(r'^(?P<id>\d+)/add_contributors/$', ProjectAddContributorsView.as_view(), name='add-contributors'),
    url(r'^(?P<id>\d+)/delete_contributors/$', ProjectDeleteContributorsView.as_view(), name='delete-contributors'),
    url(r'^verify/$', ProjectVerifyListView.as_view(), name='verify-projects-list'),
    url(r'^(?P<id>\d+)/verify/$', ProjectVerifyDetailView.as_view(), name='verify-projects-detail'),
    url(r'^(?P<id>\d+)/result/$', ProjectResultView.as_view(), name='result'),
    url(r'^(?P<id>\d+)/my_contribution/$', ProjectMyContributionView.as_view(), name='my-contribution'),
    url(r'^(?P<id>\d+)/my_inspection/$', ProjectMyInspectionView.as_view(), name='my-inspection'),
    url(r'^(?P<id>\d+)/download_result/$', ProjectResultDownloadView.as_view(), name='download-result'),
]
