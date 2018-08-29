from django.conf.urls import url

from .views import (
    TagAPIView,
)


urlpatterns = [
    url(r'^$', TagAPIView.as_view(), name='list'),
]
