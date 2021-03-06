from rest_framework import serializers
from .models import Quiz, Sitting, Question
from customuser.serializers import UserSerializer


class QuizSerializer(serializers.ModelSerializer):
    readonly_fields = 'pk'

    title = serializers.CharField(max_length=60)
    url = serializers.SlugField()

    class Meta:
        model = Quiz
        fields = (
            'id',
            'title',
            'description',
            'url',
            'random_order',
            'max_questions',
            'answers_at_end',
            'exam_paper',
            'number_attempts',
            'pass_mark',
            'success_text',
            'fail_text',
            'ranking_size',
            'draft',
            'extra_question_value'
        )


class QuizRankingSerializer(serializers.ModelSerializer):

    user = UserSerializer()
    best_score = serializers.DecimalField(decimal_places=2, max_digits=5)

    class Meta:
        model = Sitting
        fields = (
            'user',
            'best_score',
        )


class AnswerSerializer(serializers.Serializer):

    id = serializers.IntegerField()
    correct = serializers.BooleanField()
    content = serializers.CharField(max_length=500)

    class Meta:
        fields = (
            'id',
            'correct',
            'content',
        )


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = Question
        fields = (
            'id',
            'category',
            'content',
            'explanation',
            'max_time',
            'answers'
        )


class QuestionTakingSerializer(serializers.Serializer):
    question = serializers.IntegerField()
    answer = serializers.IntegerField()

    class Meta:
        fields = (
            'question',
            'answer',
        )
