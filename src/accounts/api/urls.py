from django.conf.urls import url

from rest_framework_jwt.views import refresh_jwt_token, obtain_jwt_token
from .views import RegisterAPIView, LoginAPIView, PhoneNumberOrEmailCheck
from utils.captcha.views import CaptchaAPIView

urlpatterns = [
    url(r'^register/$', RegisterAPIView.as_view(), name='register'),
    url(r'^login/$', LoginAPIView.as_view(), name='login'),
    url(r"^captcha/?$", CaptchaAPIView.as_view(), name="show_captcha"),
    url(r"^check_phone_number_or_email", PhoneNumberOrEmailCheck.as_view(), name="check_username_or_email"),
    url(r'^jwt/$', obtain_jwt_token),
    url(r'^jwt/refresh/$', refresh_jwt_token),
]
