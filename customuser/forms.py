from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from localflavor.br.forms import BRCPFField
from .models import User


class SignUpForm(UserCreationForm):

    class Meta:
        model = User

        labels = {
            'first_name': _('First Name'),
            'last_name': _('Last Name'),
            'email': _('Email'),
            'phone': _('Phone'),
            'sex': _('Sex'),
            'cpf': _('CPF'),
            'birth_date': _('Date of Birthday')
        }

        field_classes = {
            'cpf': BRCPFField
        }