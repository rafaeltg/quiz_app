from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone


SEX_CHOICES = (
    ('male', _('Male')),
    ('female', _('Female')),
    ('other', _('Other'))
)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')

        extra_fields.setdefault('is_active', True)

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create(self, **kwargs):
        return self._create_user(**kwargs)

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    first_name = models.CharField(max_length=30,
                                  blank=False,
                                  verbose_name=_('First name'))

    last_name = models.CharField(max_length=30,
                                 blank=True,
                                 verbose_name=_('Last name'))

    email = models.EmailField(verbose_name=_('Email'),
                              unique=True,
                              blank=False)

    cpf = models.CharField(max_length=14,
                           null=False,
                           blank=False,
                           verbose_name=_('CPF'))

    phone = models.CharField(max_length=15,
                             blank=True,
                             verbose_name=_('Phone'))

    sex = models.CharField(max_length=9,
                           blank=False,
                           choices=SEX_CHOICES,
                           verbose_name=_('Sex'))

    birth_date = models.DateField(verbose_name=_('Date of birth'),
                                  null=True,
                                  blank=False)

    date_joined = models.DateTimeField(verbose_name=_('Date joined'),
                                       default=timezone.now)

    is_active = models.BooleanField(verbose_name=_('Active'),
                                    editable=False,
                                    default=True)

    is_super_user = models.BooleanField(default=False,
                                        editable=False)

    is_staff = models.BooleanField(_('staff status'),
                                   default=False,
                                   editable=False,
                                   help_text=_('Designates whether the user can log into this admin site.'))

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        """
        :return: first_name plus the last_name, with a space in between.
        """
        return '{} {}'.format(self.first_name, self.last_name).strip()

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)
