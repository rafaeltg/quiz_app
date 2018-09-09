from django.forms import Form, ModelForm, EmailField, ValidationError
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from localflavor.br.forms import BRCPFField
from .models import User


class LoginForm(Form):
    email = EmailField(
        label=_('Email'),
        max_length=254
    )

    cpf = BRCPFField(
        label=_('CPF'),
        help_text=_('Digits only')
    )

    error_messages = {
        'invalid_login': _("Please enter a correct Email and CPF."),
        'inactive': _("This account is inactive."),
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        cpf = self.cleaned_data.get('cpf')

        if email is not None and cpf is not None:
            self.user_cache = authenticate(self.request, username=email, password=cpf)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy setting,
        independent of end-user authentication. This default behavior is to
        allow login by active users, and reject login by inactive users.

        If the given user cannot log in, this method should raise a
        ``forms.ValidationError``.

        If the given user may log in, this method should return None.
        """
        if not user.is_active:
            raise ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user(self):
        return self.user_cache

    def get_invalid_login_error(self):
        return ValidationError(
            self.error_messages['invalid_login'],
            code='invalid_login'
        )


class SignUpForm(ModelForm):

    class Meta:
        model = User

        fields = ('first_name', 'last_name', 'email', 'cpf', )

        labels = {
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'email': _('Email'),
            'cpf': _('CPF')
        }

        field_classes = {
            'cpf': BRCPFField
        }

        help_texts = {
            'cpf': _('Only digits')
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['cpf'])
        if commit:
            user.save()
        return user
