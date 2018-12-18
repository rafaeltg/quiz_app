from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import APIException
from rest_framework import status


class NotAllowedToTakeQuiz(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _("User not allowed to take this quiz.")
    default_code = 'not_allowed_to_take_quiz'


class MaxNumberOfAttempts(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = _("User has achieved the maximum number of attempts for this quiz.")
    default_code = 'max_number_of_attempts'
