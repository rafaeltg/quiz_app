from django.shortcuts import get_object_or_404
from rest_framework import generics
from .exceptions import NotAllowedToTakeQuiz
from .models import Quiz, Sitting, Question
from .serializers import QuizSerializer, QuizRankingSerializer, QuestionsSerializer, QuizAnswersSerializer


class QuizList(generics.ListCreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer


class QuizDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QuizSerializer


class QuizRanking(generics.ListAPIView):
    serializer_class = QuizRankingSerializer

    def get_queryset(self):
        quiz = get_object_or_404(Quiz, id=self.kwargs['pk'])

        sittings = Sitting.objects.filter(
            quiz=quiz,
            complete=True).order_by('-current_score')

        if sittings.count() > quiz.ranking_size:
            sittings = sittings[:quiz.ranking_size]

        return sittings


class QuizSitting(generics.GenericAPIView):

    def get_object(self):
        quiz = get_object_or_404(Quiz, id=self.kwargs['pk'])
        logged_in_user = self.request.user.is_authenticated()

        s = Sitting.objects.user_sitting(self.request.user, quiz) if logged_in_user else None
        if s is None:
            raise NotAllowedToTakeQuiz

        return s


class QuizQuestions(QuizSitting, generics.ListAPIView):
    serializer_class = QuestionsSerializer

    def get_queryset(self):
        sitting = self.get_object()
        return sitting.get_questions(with_answers=True)


class QuizTaking(QuizSitting, generics.CreateAPIView):
    serializer_class = QuizAnswersSerializer

    def perform_create(self, serializer):
        sitting = self.get_object()

        for answer in serializer.data:
            q_id = int(answer['question'])
            guess = int(answer['answer'])

            sitting.add_user_answer(q_id, guess)

            q = Question.objects.get_subclass(id=q_id)
            if q.check_if_correct(guess):
                sitting.add_to_score(1)
                if q_id in sitting.get_incorrect_questions:
                    sitting.remove_incorrect_question(q_id)
            else:
                sitting.add_incorrect_question(q_id)

        if len(sitting.get_user_answers) == len(sitting.questions_id()):
            sitting.mark_quiz_complete()

            serializer.data = {
                'score': sitting.score
            }
