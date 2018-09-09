from django.urls import re_path, include
from django.conf.urls import url
from .views import *


urlpatterns = [

    #  passes variable 'quiz_name' to next views
    url(regex=r'^(?P<slug>[\w-]+)/$',
        view=QuizDetailView.as_view(),
        name='quiz_start_page'),

    re_path(r'^(?P<quiz_name>[\w-]+)', include('customuser.urls')),

    url(regex=r'^(?P<quiz_name>[\w-]+)/take/$',
        view=QuizTake.as_view(),
        name='quiz_question'),

    url(regex=r'^(?P<quiz_name>[\w-]+)/ranking/$',
        view=QuizRankingView.as_view(),
        name='quiz_ranking')
]
