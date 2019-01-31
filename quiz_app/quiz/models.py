import re
import json
import decimal
from django.db import models
from django.core.exceptions import ValidationError, ImproperlyConfigured
from django.core.validators import MaxValueValidator, validate_comma_separated_integer_list
from django.conf import settings
from django.utils.translation import ugettext as _
from django.utils.timezone import now
from model_utils.managers import InheritanceManager
from customuser.models import User
from .exceptions import MaxNumberOfAttempts


class QuizManager(models.Manager):

    def __init__(self, *args, **kwargs):
        self.no_drafts = kwargs.pop('no_drafts', True)
        super(QuizManager, self).__init__()

    def get_queryset(self):
        queryset = super(QuizManager, self).get_queryset()
        if self.no_drafts:
            return queryset.filter(draft=False)
        return queryset


class Quiz(models.Model):

    title = models.CharField(verbose_name=_("Title"),
                             max_length=60,
                             blank=False)

    description = models.TextField(verbose_name=_("Description"),
                                   blank=True,
                                   help_text=_("a description of the quiz"))

    url = models.SlugField(max_length=60,
                           blank=False,
                           help_text=_("a user friendly url"),
                           verbose_name=_("user friendly url"))

    random_order = models.BooleanField(blank=False,
                                       default=False,
                                       verbose_name=_("Random Order"),
                                       help_text=_("Display the questions in a random order or as they are set?"))

    max_questions = models.PositiveIntegerField(blank=True,
                                                null=True,
                                                verbose_name=_("Max Questions"),
                                                help_text=_("Number of questions to be answered on each attempt."))

    answers_at_end = models.BooleanField(blank=False,
                                         default=False,
                                         verbose_name=_("Answers at end"),
                                         help_text=_("Correct answer is NOT shown after question. "
                                                     "Answers displayed at the end."))

    exam_paper = models.BooleanField(blank=False,
                                     default=False,
                                     verbose_name=_("Exam Paper"),
                                     help_text=_("If yes, the result of each attempt by a user will be stored. "
                                                 "Necessary for marking."))

    number_attempts = models.PositiveIntegerField(blank=True,
                                                  default=1,
                                                  verbose_name=_("Max number of attempts"),
                                                  help_text=_("If not set, users have no limit of attempts."))

    pass_mark = models.SmallIntegerField(blank=True,
                                         default=0,
                                         verbose_name=_("Pass Mark"),
                                         help_text=_("Percentage required to pass exam. 0% to 100%."),
                                         validators=[MaxValueValidator(100)])

    success_text = models.TextField(blank=True,
                                    verbose_name=_("Success Text"),
                                    help_text=_("Displayed if user passes."))

    fail_text = models.TextField(blank=True,
                                 verbose_name=_("Fail Text"),
                                 help_text=_("Displayed if user fails."))

    ranking_size = models.SmallIntegerField(blank=True,
                                            default=10,
                                            verbose_name=_("Ranking size"),
                                            help_text=_("Number of players to be displayed in the ranking list."))

    draft = models.BooleanField(blank=True,
                                default=False,
                                verbose_name=_("Draft"),
                                help_text=_("If yes, the quiz is not displayed in the quiz list and can only be "
                                            "taken by users who can edit quizzes."))

    extra_question_value = models.DecimalField(default=25.0,
                                               max_digits=5,
                                               decimal_places=2,
                                               verbose_name=_("Extra Questions Value (in %)"),
                                               help_text=_("Extra questions value in %."))

    objects = QuizManager(no_drafts=True)
    all_objects = QuizManager()

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if self.number_attempts == 1:
            self.exam_paper = True

        if self.pass_mark > 100:
            raise ValidationError('%s is above 100' % self.pass_mark)

        super(Quiz, self).save(force_insert, force_update, *args, **kwargs)

    class Meta:
        verbose_name = _("Quiz")
        verbose_name_plural = _("Quizzes")

    def __str__(self):
        return self.title

    def get_questions(self):
        return self.questions.all().select_subclasses()

    @property
    def get_max_score(self):
        return self.get_questions().count()

    def get_ranking(self):
        sittings = Sitting.objects.filter(quiz=self, complete=True) \
            .values('user') \
            .annotate(best_score=models.Max('score')) \
            .order_by('-best_score')[:self.ranking_size]

        for s in sittings:
            s['user'] = User.objects.get(pk=s['user'])

        return sittings


class CategoryManager(models.Manager):

    def new_category(self, category):
        new_category = self.create(category=re.sub('\s+', '-', category).lower())
        new_category.save()
        return new_category


class Category(models.Model):

    category = models.CharField(verbose_name=_("Category"),
                                max_length=250,
                                blank=True,
                                unique=True,
                                null=True)

    objects = CategoryManager()

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.category


class Question(models.Model):
    """
    Base class for all question types.
    """

    quiz = models.ManyToManyField(Quiz,
                                  verbose_name=_("Quiz"),
                                  related_name='questions',
                                  blank=True)

    category = models.ForeignKey(Category,
                                 verbose_name=_("Category"),
                                 blank=True,
                                 null=True,
                                 on_delete=models.CASCADE)

    content = models.CharField(max_length=1000,
                               blank=False,
                               help_text=_("Enter the question text that you want displayed"),
                               verbose_name=_('Question'))

    explanation = models.TextField(max_length=2000,
                                   blank=True,
                                   help_text=_("Explanation to be shown after the question has been answered."),
                                   verbose_name=_('Explanation'))

    max_time = models.IntegerField(verbose_name=_('Time limit'),
                                   default=60,
                                   help_text=_("Time limit to answer the question in seconds."))

    objects = InheritanceManager()

    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")
        ordering = ['category']

    def __str__(self):
        return self.content


class SittingManager(models.Manager):

    def new_sitting(self, user, quiz):
        if quiz.random_order is True:
            question_set = quiz.questions.all().select_subclasses().order_by('?')
        else:
            question_set = quiz.questions.all().select_subclasses()

        question_set = [item.id for item in question_set]

        if len(question_set) == 0:
            raise ImproperlyConfigured('Question set of the quiz is empty. Please configure questions properly')

        if quiz.max_questions and (quiz.max_questions < len(question_set)):
            question_set = question_set[:quiz.max_questions]

        questions = ",".join(map(str, question_set)) + ","

        new_sitting = self.create(user=user,
                                  quiz=quiz,
                                  question_order=questions,
                                  question_list=questions,
                                  incorrect_questions="",
                                  incorrect_extra_questions="",
                                  score=0,
                                  start=now(),
                                  complete=False,
                                  user_answers='{}',
                                  user_extra_answers='{}')
        return new_sitting

    def user_sitting(self, user, quiz):
        if quiz.number_attempts:
            if quiz.number_attempts < self.filter(user=user, quiz=quiz, complete=True).count():
                raise MaxNumberOfAttempts

        try:
            sitting = self.get(user=user, quiz=quiz, complete=False)
        except Sitting.DoesNotExist:
            sitting = self.new_sitting(user, quiz)
        except Sitting.MultipleObjectsReturned:
            sitting = self.filter(user=user, quiz=quiz, complete=False).order_by('-start').first()
        return sitting


class Sitting(models.Model):
    """
    Used to store the progress of logged in users sitting a quiz.
    Sitting deleted when quiz finished unless quiz.exam_paper is true.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             verbose_name=_("User"),
                             on_delete=models.CASCADE)

    quiz = models.ForeignKey(Quiz,
                             verbose_name=_("Quiz"),
                             on_delete=models.CASCADE)

    # list of integer pks of all the questions in the quiz, in order.
    question_order = models.CharField(max_length=1024,
                                      verbose_name=_("Question Order"),
                                      validators=[validate_comma_separated_integer_list])

    # list of integers which represent id's of the unanswered questions in csv format.
    question_list = models.CharField(max_length=1024,
                                     verbose_name=_("Question List"),
                                     validators=[validate_comma_separated_integer_list])

    incorrect_questions = models.CharField(max_length=1024,
                                           blank=True,
                                           verbose_name=_("Incorrect questions"),
                                           validators=[validate_comma_separated_integer_list])

    extra_questions_list = models.CharField(max_length=1024,
                                            blank=True,
                                            verbose_name=_("Extra Question List"),
                                            validators=[validate_comma_separated_integer_list])

    incorrect_extra_questions = models.CharField(max_length=1024,
                                                 blank=True,
                                                 verbose_name=_("Incorrect extra questions"),
                                                 validators=[validate_comma_separated_integer_list])

    score = models.DecimalField(verbose_name=_("Score"),
                                decimal_places=2,
                                max_digits=6)

    complete = models.BooleanField(default=False,
                                   blank=False,
                                   verbose_name=_("Complete"))

    # json object in which the question PK is stored with the answer the user gave.
    user_answers = models.TextField(blank=True,
                                    default='{}',
                                    verbose_name=_("User Answers"))

    user_extra_answers = models.TextField(blank=True,
                                          default='{}',
                                          verbose_name=_("User Extra Answers"))

    start = models.DateTimeField(auto_now_add=True,
                                 verbose_name=_("Start"))

    end = models.DateTimeField(null=True,
                               blank=True,
                               verbose_name=_("End"))

    objects = SittingManager()

    class Meta:
        permissions = (("view_sittings", _("Can see completed exams.")),)

    def questions_id(self):
        return [int(n) for n in self.question_order.split(',') if n]

    def calculate_score(self):
        max_time = 60 * len(self.questions_id())
        elapsed_time = (self.end - self.start).seconds
        t = elapsed_time / max_time

        score = self.percent_correct

        if t > .25:
            if t <= .5:
                score *= .75
            elif t <= .75:
                score *= .5
            else:
                score *= .25

        self.score = round(score * 100.0, 2)

    def calculate_score_extra(self):
        extra_score = self.quiz.extra_question_value * decimal.Decimal(self.percent_correct_extra)
        self.score = round(self.score + extra_score, 2)
        self.save()

    @property
    def percent_correct_extra(self):
        total = len(self.get_user_extra_answers())

        if total == 0:
            return 0.0

        corrects = total - len(self.get_incorrect_extra_questions())

        if corrects > total:
            return 1.0

        return corrects / total

    @property
    def percent_correct(self):
        total = len(self.questions_id())

        if total == 0:
            return 0.0

        corrects = total - len(self.get_incorrect_questions())

        if corrects > total:
            return 1.0

        return corrects / total

    def mark_quiz_complete(self):
        self.complete = True
        self.end = now()
        self.calculate_score()
        self.save()

    def get_incorrect_questions(self):
        return [int(q) for q in self.incorrect_questions.split(',') if q]

    def remove_incorrect_question(self, question_id):
        current = self.get_incorrect_questions()

        if question_id in current:
            current.remove(question_id)
            self.incorrect_questions = ','.join(map(str, current))
            self.save()

    def add_incorrect_question(self, question_id):
        current = self.get_incorrect_questions()

        if question_id not in current:
            current.append(question_id)
            self.incorrect_questions = ','.join(map(str, current))
            self.save()

    def get_incorrect_extra_questions(self):
        return [int(q) for q in self.incorrect_extra_questions.split(',') if q]

    def remove_incorrect_extra_question(self, question_id):
        current = self.get_incorrect_extra_questions()

        if question_id in current:
            current.remove(question_id)
            self.incorrect_extra_questions = ','.join(map(str, current))
            self.save()

    def add_incorrect_extra_question(self, question_id):
        current = self.get_incorrect_extra_questions()

        if question_id not in current:
            current.append(question_id)
            self.incorrect_extra_questions = ','.join(map(str, current))
            self.save()

    @property
    def check_if_passed(self):
        return self.percent_correct >= self.quiz.pass_mark

    @property
    def result_message(self):
        return self.quiz.success_text if self.check_if_passed else self.quiz.fail_text

    def add_user_answer(self, question_id, guess):
        current = json.loads(self.user_answers)
        current[question_id] = guess
        self.user_answers = json.dumps(current)
        self.save()

    def add_user_extra_answer(self, question_id, guess):
        current = json.loads(self.user_extra_answers)
        current[question_id] = guess
        self.user_extra_answers = json.dumps(current)
        self.save()

    def get_user_answers(self):
        return json.loads(self.user_answers)

    def get_user_extra_answers(self):
        return json.loads(self.user_extra_answers)

    def get_questions(self, with_answers=False):
        question_ids = self.questions_id()
        questions = sorted(
            self.quiz.questions.filter(id__in=question_ids).select_subclasses(),
            key=lambda q: question_ids.index(q.id))

        obj = []
        for question in questions:
            obj.append(
                {
                    'id': question.id,
                    'category': question.category,
                    'content': question.content,
                    'explanation': question.explanation,
                    'max_time': question.max_time,
                    'answers': question.get_answers() if with_answers else []
                })

        return obj
