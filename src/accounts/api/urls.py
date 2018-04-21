from django.conf.urls import url

from rest_framework_jwt.views import refresh_jwt_token, obtain_jwt_token
from .views import RegisterAPIView, LoginAPIView


urlpatterns = [
    url(r'^register/$', RegisterAPIView.as_view(), name='register'),
    url(r'^login/$', LoginAPIView.as_view(), name='login'),
    url(r'^jwt/$', obtain_jwt_token),
    url(r'^jwt/refresh/$', refresh_jwt_token),
]
