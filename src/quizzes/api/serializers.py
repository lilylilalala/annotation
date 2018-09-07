import csv

from rest_framework import serializers
from rest_framework.reverse import reverse as api_reverse

from quizzes.models import Quiz, Question, Answer
from targets.api.serializers import TargetSerializer
from tags.api.serializers import TagBriefSerializer
from annotation.utils import get_filename_ext


class QuizSerializer(serializers.ModelSerializer):
    tags_detail = serializers.SerializerMethodField(read_only=False)
    target = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Quiz
        fields = [
            'id',
            'name',
            'tags',
            'tags_detail',
            'quiz_target',
            'target',
            'quiz_file',
            'label_file',
            'founder',
            'contributors',
            'description',
            'updated',
        ]
        read_only_fields = ['founder', 'contributors']

    def get_tags_detail(self, obj):
        tags_queryset = obj.tags
        return TagBriefSerializer(tags_queryset, many=True).data

    def get_target(self, obj):
        target = obj.quiz_target
        return TargetSerializer(target).data


class QuestionSerializer(serializers.ModelSerializer):
    text_content = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Question
        fields = [
            'id',
            'quiz',
            'text_content',
            'label',
            'timestamp',
        ]
        read_only_fields = ['quiz', 'label']

    def get_text_content(self, obj):
        path = obj.file_path
        name, ext = get_filename_ext(path)
        if ext == '.csv':
            reader = csv.DictReader(open(path, encoding='utf-8'))
            for i, row in enumerate(reader):
                if i == 0:
                    content = row
        else:
            content = ''
        return content


class AnswerSerializer(serializers.ModelSerializer):
    quiz = serializers.SerializerMethodField(read_only=True)
    target = serializers.SerializerMethodField(read_only=True)
    text_content = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Answer
        fields = [
            'id',
            'quiz',
            'target',
            'text_content',
            'label',
            'updated',
        ]
        read_only_fields = ['quiz']

    def get_quiz(self, obj):
        return obj.question.quiz.id

    def get_target(self, obj):
        target = obj.question.quiz.quiz_target
        return TargetSerializer(target).data

    def get_text_content(self, obj):
        path = obj.question.file_path
        name, ext = get_filename_ext(path)
        if ext == '.csv':
            reader = csv.DictReader(open(path, encoding='utf-8'))
            for i, row in enumerate(reader):
                if i == 0:
                    content = row
        else:
            content = ''
        return content