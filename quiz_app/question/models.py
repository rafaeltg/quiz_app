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
                'correct': self.correct,
                'content': 'True'
            },
            {
                'id': 1,
                'correct': not self.correct,
                'content': 'False'
            }
        ]

    def answer_choice_to_string(self, guess):
        return str(guess)

    class Meta:
        verbose_name = _("True/False Question")
        verbose_name_plural = _("True/False Questions")
        ordering = ['category']


ANSWER_ORDER_CHOICES = (
    ('content', _('Content')),
    ('random', _('Random')),
    ('none', _('None'))
)


class MCQuestion(Question):

    answer_order = models.CharField(max_length=30,
                                    null=True,
                                    blank=True,
                                    choices=ANSWER_ORDER_CHOICES,
                                    help_text=_("The order in which multiple choice answer options are displayed "
                                                "to the user"),
                                    verbose_name=_("Answer Order"))

    def check_if_correct(self, guess):
        answer = self.answers.get(id=guess)
        return answer.correct is True

    def order_answers(self, queryset):
        if self.answer_order is None:
            return queryset.all()
        if self.answer_order == 'content':
            return queryset.order_by('content').all()
        if self.answer_order == 'random':
            return queryset.order_by('?').all()
        return queryset.all()

    def get_answers(self):
        answers = []

        for a in self.order_answers(self.answers):
            answers.append({
                'id': a.id,
                'correct': a.correct,
                'content': a.content
            })

        return answers

    def answer_choice_to_string(self, guess):
        return self.answers.get(id=guess).content

    class Meta:
        verbose_name = _("Multiple Choice Question")
        verbose_name_plural = _("Multiple Choice Questions")


class Answer(models.Model):

    question = models.ForeignKey(MCQuestion,
                                 verbose_name=_("Question"),
                                 related_name='answers',
                                 on_delete=models.CASCADE)

    content = models.CharField(max_length=500,
                               blank=False,
                               help_text=_("Enter the answer text that you want displayed"),
                               verbose_name=_("Content"))

    correct = models.BooleanField(blank=False,
                                  default=False,
                                  help_text=_("Is this a correct answer?"),
                                  verbose_name=_("Correct"))

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = _("Answer")
        verbose_name_plural = _("Answers")
