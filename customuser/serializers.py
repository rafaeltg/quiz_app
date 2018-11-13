from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, exceptions
from rest_framework.validators import UniqueValidator
from .models import User


class UserSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())])

    password = serializers.CharField(
        max_length=128,
        write_only=True)

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'phone',
            'birth_date',
            'password')
        read_only_fields = ('email', 'cpf',)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, style={'input_type': 'password'})

    class Meta:
        fields = (
            'email',
            'password'
        )

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


class TokenSerializer(serializers.Serializer):

    user = serializers.IntegerField()
    token = serializers.CharField(max_length=40)

    class Meta:
        fields = (
            'user',
            'token'
        )
