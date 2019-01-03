from django.conf.urls import url
from .views import *


urlpatterns = [
    url(regex=r'^(?P<pk>[0-9]+)$',
        view=QuizDetail.as_view(),
        name='quiz-detail'),

    url(regex=r'^(?P<pk>[0-9]+)/ranking$',
        view=QuizRanking.as_view(),
        name='quiz-ranking'),

    url(regex=r'^(?P<pk>[0-9]+)/questions$',
        view=QuizQuestions.as_view(),
        name='quiz-questions'),

    url(regex=r'^(?P<pk>[0-9]+)/taking$',
        view=QuizTaking.as_view(),
        name='quiz-taking'),

    url(regex=r'^(?P<pk>[0-9]+)/taking-extra$',
        view=QuizTakingExtra.as_view(),
        name='quiz-taking-extra'),

    url(regex='^$',
        view=QuizList.as_view(),
        name='quiz-list')
]
