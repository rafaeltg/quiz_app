from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from .exceptions import NotAllowedToTakeQuiz
from .models import Quiz, Sitting, Question
from .serializers import QuizSerializer, QuizRankingSerializer, QuestionSerializer, QuestionTakingSerializer


class QuizList(generics.ListCreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer


class QuizDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = (IsAuthenticated,)


class QuizRanking(generics.ListAPIView):
    serializer_class = QuizRankingSerializer

    def get_queryset(self):
        quiz = get_object_or_404(Quiz, id=self.kwargs['pk'])
        return quiz.get_ranking()


class QuizSitting(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        quiz = get_object_or_404(Quiz, id=self.kwargs['pk'])
        logged_in_user = self.request.user.is_authenticated

        s = Sitting.objects.user_sitting(self.request.user, quiz) if logged_in_user else None
        if s is None:
            raise NotAllowedToTakeQuiz

        return s


class QuizQuestions(QuizSitting, generics.ListAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        sitting = self.get_object()
        return sitting.get_questions(with_answers=True)


class QuizTaking(QuizSitting, generics.CreateAPIView):
    serializer_class = QuestionTakingSerializer

    def get_serializer(self, instance=None, data=None, many=False, partial=False):
        return super(QuizTaking, self).get_serializer(instance=instance, data=data, many=True, partial=partial)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sitting = self.get_object()

        for answer in serializer.data:
            q_id = int(answer['question'])
            guess = int(answer['answer'])

            sitting.add_user_answer(q_id, guess)

            q = Question.objects.get_subclass(id=q_id)
            if q.check_if_correct(guess):
                sitting.add_to_score(1)
                sitting.remove_incorrect_question(q_id)
            else:
                sitting.add_incorrect_question(q_id)

        sitting.mark_quiz_complete()
        data = {
            'score': sitting.score,
            'success_text': sitting.quiz.success_text,
            'fail_text': sitting.quiz.fail_text
        }

        return Response(
            data=data,
            status=HTTP_201_CREATED,
            headers=self.get_success_headers(serializer.data))


class QuizTakingExtra(QuizTaking):

    def get_object(self):
        quiz = get_object_or_404(Quiz, id=self.kwargs['pk'])

        if not self.request.user.is_authenticated:
            raise NotAllowedToTakeQuiz

        user = self.request.user

        try:
            sitting = Sitting.objects.get(user=user, quiz=quiz, complete=True)
        except Sitting.MultipleObjectsReturned:
            sitting = Sitting.objects.filter(user=user, quiz=quiz, complete=True).order_by('-end').first()
        except Sitting.DoesNotExist:
            raise NotAllowedToTakeQuiz

        return sitting

