from django.conf.urls import url
from .views import *


urlpatterns = [
    url(regex='',
        view=QuizList.as_view(),
        name='quiz-list'),

    url(regex=r'<int:pk>/$',
        view=QuizDetail.as_view(),
        name='quiz-detail'),

    url(regex=r'<int:pk>/ranking/$',
        view=QuizRanking.as_view(),
        name='quiz-ranking'),

    url(regex=r'<int:pk>/questions/$',
        view=QuizQuestions.as_view(),
        name='quiz-questions'),

    url(regex=r'<int:pk>/taking/$',
        view=QuizTaking.as_view(),
        name='quiz-taking')
]
