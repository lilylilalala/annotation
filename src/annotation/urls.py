"""annotation URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.conf.urls import url, include
from django.contrib import admin

schema_view = get_schema_view(
    openapi.Info(
        title="Annotation API",
        default_version='v1',
        description="Test description",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=None), name='schema-redoc'),
    url(r'^admin/', admin.site.urls),
    url(r'^api/auth/', include('accounts.api.urls', namespace='api-auth')),
    url(r'^api/users/', include('accounts.api.users.urls', namespace='api-users')),
    url(r'^api/projects/', include('projects.api.urls', namespace='api-projects')),
    url(r'^api/tasks/', include('tasks.api.urls', namespace='api-tasks')),
    url(r'^api/targets/', include('targets.api.urls', namespace='api-targets')),
    url(r'^api/tags/', include('tags.api.urls', namespace='api-tags')),
    url(r'^api/quizzes/', include('quizzes.api.urls', namespace='api-quizzes')),
]
