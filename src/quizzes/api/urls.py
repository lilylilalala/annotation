from django.conf.urls import url

from .views import (
    QuizAPIView,
    QuestionAPIView,
    AnswerAPIView,
)


urlpatterns = [
    url(r'^$', QuizAPIView.as_view(), name='list'),
    url(r'^(?P<id>\d+)/$', QuestionAPIView.as_view(), name='question-list'),
    url(r'^(?P<id>\d+)/answer/$', AnswerAPIView.as_view(), name='answer'),
]
