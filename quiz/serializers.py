from rest_framework import serializers
from .models import Quiz, Sitting, Question


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
            'single_attempt',
            'pass_mark',
            'success_text',
            'fail_text',
            'ranking_size',
            'draft',
        )


class QuizRankingSerializer(serializers.ModelSerializer):
    readonly_fields = 'pk'

    class Meta:
        model = Sitting
        fields = (
            'user',
            'score',
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
