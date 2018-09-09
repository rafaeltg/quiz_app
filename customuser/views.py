# accounts/views.py
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import views
from .forms import LoginForm, SignUpForm


class LoginView(views.LoginView):
    form_class = LoginForm
    success_url = reverse_lazy('quiz_question')
    template_name = 'login.html'


class SignUpView(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('quiz_question')
    template_name = 'signup.html'
