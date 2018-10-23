import csv

from rest_framework import serializers

from quizzes.models import Quiz, Question, Answer, QuizContributor, QuestionType
from targets.api.serializers import TargetSerializer, TargetTypeSerializer
from tags.api.serializers import TagBriefSerializer
from annotation.utils import get_filename_ext


class QuizSerializer(serializers.ModelSerializer):
    tags_detail = serializers.SerializerMethodField(read_only=True)
    quiz_type_name = serializers.SerializerMethodField(read_only=True)
    target = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Quiz
        fields = [
            'id',
            'name',
            'tags',
            'tags_detail',
            'quiz_type',
            'quiz_type_name',
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

    def validate(self, data):
        quiz_file = data.get('quiz_file')
        label_file = data.get('label_file')
        if quiz_file and label_file:
            return data
        elif quiz_file or label_file:
            raise serializers.ValidationError("Please add both quiz_file and label_file!")
        return data

    def get_tags_detail(self, obj):
        tags_queryset = obj.tags
        return TagBriefSerializer(tags_queryset, many=True).data

    def get_quiz_type_name(self, obj):
        return obj.quiz_type.chinese_name

    def get_target(self, obj):
        target = obj.quiz_target
        return TargetSerializer(target).data


class QuestionSerializer(serializers.ModelSerializer):
    text_content = serializers.SerializerMethodField(read_only=True)
    question_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Question
        fields = [
            'id',
            'quiz',
            'text_content',
            'label',
            'timestamp',
            'question_id',
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


class QuizRecordSerializer(serializers.ModelSerializer):
    contributor_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = QuizContributor
        fields = [
            'id',
            'contributor',
            'contributor_name',
            'status',
            'accuracy',
            'updated',
            'timestamp',
        ]

    def get_contributor_name(self, obj):
        return obj.contributor.full_name


class QuestionsAddSerializer(QuizSerializer):

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
        read_only_fields = ['founder', 'contributors', 'name', 'tags', 'quiz_target', 'description', ]


class AnswerUpdateSerializer(serializers.ModelSerializer):
    quiz = serializers.SerializerMethodField(read_only=True)
    target = serializers.SerializerMethodField(read_only=True)
    text_content = serializers.SerializerMethodField(read_only=True)
    previous_id = serializers.SerializerMethodField(read_only=True)
    next_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Answer
        fields = [
            'id',
            'quiz',
            'target',
            'text_content',
            'label',
            'updated',
            'previous_id',
            'next_id',
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

    def get_previous_id(self, obj):
        if obj.quiz_contributor:
            my_quiz = Answer.objects.filter(quiz_contributor=obj.quiz_contributor)
            previous = my_quiz.filter(created__lt=obj.created).order_by('-created').first()
            if previous:
                return previous.id
        return None

    def get_next_id(self, obj):
        if obj.quiz_contributor:
            my_quiz = Answer.objects.filter(quiz_contributor=obj.quiz_contributor)
            previous = my_quiz.filter(created__gt=obj.created).order_by('created').first()
            if previous:
                return previous.id
        return None


class QuestionSubmitSerializer(serializers.ModelSerializer):
    quiz_name = serializers.SerializerMethodField(read_only=True)
    contributor_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = QuizContributor
        fields = [
            'id',
            'quiz',
            'quiz_name',
            'contributor',
            'contributor_name',
            'progress',
            'status',
            'accuracy',
            'updated',
            'timestamp',
        ]
        read_only_fields = ['quiz', 'contributor', 'status', 'accuracy']

    def get_quiz_name(self, obj):
        return obj.quiz.name

    def get_contributor_name(self, obj):
        return obj.contributor.full_name


class QuestionTypeSerializer(serializers.ModelSerializer):
    target_type = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = QuestionType
        fields = [
            'id',
            'name',
            'chinese_name',
            'target_type',
        ]

    def get_target_type(self, obj):
        target_type = obj.type
        return TargetTypeSerializer(target_type).data


class QuizDetailSerializer(QuizSerializer):

    class Meta:
        model = Quiz
        fields = [
            'id',
            'name',
            'tags',
            'tags_detail',
            'quiz_type',
            'quiz_type_name',
            'quiz_target',
            'target',
            'quiz_file',
            'label_file',
            'founder',
            'contributors',
            'description',
            'updated',
            'timestamp',
        ]