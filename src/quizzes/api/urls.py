from django.conf.urls import url

from .views import (
    QuizAPIView,
    QuizAPIDetailView,
    QuestionAPIView,
    AnswerAPIView,
    QuizRecordView,
    AnswerUpdateAPIView,
    QuestionSubmitAPIView,
    QuestionTypeAPIView,
    QuestionsAddAPIView,
    QuestionDownloadAPIView,
)


urlpatterns = [
    url(r'^$', QuizAPIView.as_view(), name='list'),
    url(r'^(?P<id>\d+)/$', QuizAPIDetailView.as_view(), name='detail'),
    url(r'^(?P<id>\d+)/questions/$', QuestionAPIView.as_view(), name='question-list'),
    url(r'^(?P<id>\d+)/add_questions/$', QuestionsAddAPIView.as_view(), name='question-add'),
    url(r'^(?P<id>\d+)/answer/$', AnswerAPIView.as_view(), name='answer'),
    url(r'^(?P<id>\d+)/records/$', QuizRecordView.as_view(), name='record-list'),
    url(r'^(?P<id>\d+)/answer/(?P<answerid>\d+)/update/$', AnswerUpdateAPIView.as_view(), name='answer-update'),
    url(r'^(?P<id>\d+)/answer/submit/$', QuestionSubmitAPIView.as_view(), name='answer-submit'),
    url(r'^types/$', QuestionTypeAPIView.as_view(), name='type_list'),
    url(r'^(?P<id>\d+)/file_download/$', QuestionDownloadAPIView.as_view(), name='question_file_download'),
]
