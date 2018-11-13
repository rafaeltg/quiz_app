from django.urls import path
from django.conf.urls import url
from .views import UserDetailView, LoginView, SignUpView


urlpatterns = [
    path('login',
         LoginView.as_view(),
         name='user-login'),

    path('signup',
         SignUpView.as_view(),
         name='user-signup'),

    url(regex='',
        view=UserDetailView.as_view(),
        name='user-detail')
]
