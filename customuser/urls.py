from django.urls import path
from .views import LoginView, SignUpView


urlpatterns = [
    path('login/', LoginView.as_view(), name='user_login'),
    path('signup/', SignUpView.as_view(), name='user_signup'),
]
