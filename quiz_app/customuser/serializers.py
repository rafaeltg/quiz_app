from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, exceptions
from rest_framework.validators import UniqueValidator
from .models import User


class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        required=False,
        max_length=128,
        write_only=True)

    cpf = serializers.CharField(
        required=True,
        max_length=24,
        validators=[UniqueValidator(queryset=User.objects.all())])

    email = serializers.EmailField(
        required=False,
        validators=[UniqueValidator(queryset=User.objects.exclude(email__isnull=True).all())])

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'cpf',
            'phone',
            'birth_date',
            'password')
        read_only_fields = ('cpf',)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):

    cpf = serializers.CharField(required=True, max_length=14)
    password = serializers.CharField(required=True, style={'input_type': 'password'})

    class Meta:
        fields = (
            'cpf',
            'password'
        )

    def _validate_credentials(self, cpf, password):
        if cpf and password:
            return authenticate(self.context['request'], cpf=cpf, password=password)

        raise exceptions.ValidationError(_('Must include "cpf" and "password".'))

    def validate(self, attrs):
        cpf = attrs.get('cpf')
        password = attrs.get('password')

        user = self._validate_credentials(cpf, password)

        if user is None:
            raise exceptions.ValidationError(_('Unable to log in with provided credentials.'))

        if not user.is_active:
            raise exceptions.ValidationError(_('User account is disabled.'))

        attrs['user'] = user
        return attrs


class TokenSerializer(serializers.Serializer):

    user = UserSerializer()
    token = serializers.CharField(max_length=40)

    class Meta:
        fields = (
            'user',
            'token'
        )
