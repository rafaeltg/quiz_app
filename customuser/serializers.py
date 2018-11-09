from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode as uid_decoder
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_text

from rest_framework import serializers, exceptions
from rest_framework.exceptions import ValidationError

from rest_framework.authtoken.models import Token
from .models import User
from .utils import import_callable


class UserDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'pk',
            'first_name',
            'last_name',
            'email',
            'cpf')
        read_only_fields = ('email', 'cpf', )


class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(style={'input_type': 'password'})

    def _validate_email(self, email, password):
        user = None

        if email and password:
            user = authenticate(self.context['request'], email=email, password=password)
        else:
            raise exceptions.ValidationError(_('Must include "email" and "password".'))

        return user

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = self._validate_email(email, password)

        if user is None:
            raise exceptions.ValidationError(_('Unable to log in with provided credentials.'))

        if not user.is_active:
            raise exceptions.ValidationError(_('User account is disabled.'))

        attrs['user'] = user
        return attrs


class TokenSerializer(serializers.ModelSerializer):
    """
    Serializer for Token model.
    """

    class Meta:
        model = Token
        fields = ('key',)
