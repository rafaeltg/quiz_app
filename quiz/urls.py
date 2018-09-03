from django.conf.urls import url
from .views import *


urlpatterns = [

    #  passes variable 'quiz_name' to quiz_take and quiz_ranking view
    url(regex=r'^(?P<slug>[\w-]+)/$',
        view=QuizDetailView.as_view(),
        name='quiz_start_page'),

    url(regex=r'^(?P<quiz_name>[\w-]+)/take/$',
        view=QuizTake.as_view(),
        name='quiz_question'),

    url(regex=r'^(?P<quiz_name>[\w-]+)/ranking/$',
        view=QuizRankingView.as_view(),
        name='quiz_ranking')
]