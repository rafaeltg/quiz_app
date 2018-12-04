from django.utils.translation import ugettext as _
from django.db import models
from quiz.models import Question


class TFQuestion(Question):

    correct = models.BooleanField(blank=False,
                                  default=False,
                                  help_text=_("Tick this if the question is true. Leave it blank for false."),
                                  verbose_name=_("Correct"))

    def check_if_correct(self, guess):
        if guess == 0:
            guess_bool = True
        elif guess == 1:
            guess_bool = False
        else:
            return False

        return guess_bool == self.correct

    def get_answers(self):
        return [
            {
                'id': 0,
                'correct': self.check_if_correct("True"),
                'content': 'True'
            },
            {
                'id': 1,
                'correct': self.check_if_correct("False"),
                'content': 'False'
            }
        ]

    def answer_choice_to_string(self, guess):
        return str(guess)

    class Meta:
        verbose_name = _("True/False Question")
        verbose_name_plural = _("True/False Questions")
        ordering = ['category']
