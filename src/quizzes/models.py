import os
import csv

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.storage import FileSystemStorage
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.validators import MinValueValidator, MaxValueValidator

from annotation.utils import get_filename_ext, random_string_generator
from targets.models import Target, TargetType
from tags.models import Tag


User = get_user_model()


def upload_quiz_file_path(instance, filename):
    name, ext = get_filename_ext(filename)
    while True:
        new_filename = random_string_generator()
        if new_filename not in os.listdir(settings.MEDIA_ROOT):
            break
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return final_filename


class QuestionType(models.Model):
    name = models.CharField(max_length=128, unique=True)
    chinese_name = models.CharField(max_length=128, unique=True)
    type = models.ForeignKey(TargetType, related_name='related_question_types')

    def __str__(self):
        return str(self.name)


class Quiz(models.Model):
    name = models.CharField(max_length=128, unique=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='tagged_quizzes')
    quiz_type = models.ForeignKey(QuestionType)
    quiz_target = models.ForeignKey(Target)
    quiz_file = models.FileField(
        upload_to=upload_quiz_file_path,
        storage=FileSystemStorage(location=settings.QUIZ_ROOT, base_url=settings.QUIZ_URL),
        blank=True,
        null=True,
    )
    label_file = models.FileField(
        upload_to=upload_quiz_file_path,
        storage=FileSystemStorage(location=settings.LABEL_ROOT, base_url=settings.LABEL_URL),
        blank=True,
        null=True,
    )
    founder = models.ForeignKey(User, related_name='founded_quizzes')
    contributors = models.ManyToManyField(User, related_name='answered_quizzes', through='QuizContributor')
    description = models.TextField(blank=True)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id) + '_' + self.name

    @property
    def owner(self):
        return self.founder

    @property
    def contributor_number(self):
        return self.quizcontributor_set.filter(status='submitted').count()


class Question(models.Model):
    quiz = models.ForeignKey(Quiz)
    file_path = models.CharField(max_length=255)
    label = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id) + '_' + self.quiz.name


class QuizContributor(models.Model):
    quiz = models.ForeignKey(Quiz)
    contributor = models.ForeignKey(User)
    accuracy = models.DecimalField(
        max_digits=8, decimal_places=7, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    status = models.CharField(max_length=255, blank=True, default='in progress')
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id) + '_' + str(self.quiz)

    @property
    def quantity(self):
        return self.answer_set.count()

    @property
    def is_completed(self):
        if self.answer_set.filter(label=''):
            return False
        return True

    @property
    def progress(self):
        num_of_answers = self.answer_set.count()
        completed = self.answer_set.exclude(label='').count()
        try:
            return '%d%%' % (completed/num_of_answers*100)
        except:
            return '0%'


class Answer(models.Model):
    question = models.ForeignKey(Question)
    label = models.CharField(max_length=255, blank=True)
    quiz_contributor = models.ForeignKey(QuizContributor)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    created = models.DateTimeField(null=True)


def create_questions(instance):
    name, ext = get_filename_ext(instance.quiz_file.name)
    quiz_file_path = os.path.join(settings.QUIZ_ROOT, instance.quiz_file.name)
    quiz_file_dir = os.path.join(settings.QUIZ_ROOT, name)
    label_file_path = os.path.join(settings.LABEL_ROOT, instance.label_file.name)
    os.mkdir(quiz_file_dir)

    if ext == '.csv':
        inner_dir_name = '%s' % instance.name
        quiz_file_dir = os.path.join(quiz_file_dir, inner_dir_name)
        os.mkdir(quiz_file_dir)
        quiz_reader = csv.DictReader(open(quiz_file_path, encoding='utf-8'))
        label_reader = csv.DictReader(open(label_file_path, encoding='utf-8'))

        for (quiz_row, label_row) in zip(quiz_reader, label_reader):
            if quiz_row['\ufeffid'] == label_row['\ufeffid']:
                file_name = '%s.csv' % quiz_row['\ufeffid']
                final_quiz_file_path = os.path.join(quiz_file_dir, file_name)
                f = open(final_quiz_file_path, 'w', newline='', encoding='utf-8')
                writer = csv.DictWriter(f, dialect='excel', fieldnames=quiz_reader.fieldnames)
                writer.writeheader()
                writer.writerow(quiz_row)
                Question.objects.create(
                    quiz=instance,
                    file_path=final_quiz_file_path,
                    label=label_row['label'],
                )


@receiver(post_save, sender=Quiz)
def create_questions_receiver(sender, instance, *args, **kwargs):
    if instance.quiz_file:
        create_questions(instance)


@receiver(post_save, sender=QuizContributor)
def create_answers_receiver(sender, instance, created, *args, **kwargs):
    if created:
        for question in instance.quiz.question_set.all():
            Answer.objects.create(quiz_contributor=instance, question=question)


