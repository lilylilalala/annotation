# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-10 14:10
from __future__ import unicode_literals

from django.conf import settings
import django.core.files.storage
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import quizzes.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('targets', '0001_initial'),
        ('tags', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=255)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_path', models.CharField(max_length=255)),
                ('label', models.CharField(blank=True, max_length=255)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('chinese_name', models.CharField(max_length=128, unique=True)),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_question_types', to='targets.TargetType')),
            ],
        ),
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('quiz_file', models.FileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(base_url='/media/quiz/', location='C:\\Users\\Underwood\\PycharmProjects\\annotation\\media\\quiz'), upload_to=quizzes.models.upload_quiz_file_path)),
                ('label_file', models.FileField(blank=True, null=True, storage=django.core.files.storage.FileSystemStorage(base_url='/media/quiz/label/', location='C:\\Users\\Underwood\\PycharmProjects\\annotation\\media\\quiz\\label'), upload_to=quizzes.models.upload_quiz_file_path)),
                ('description', models.TextField(blank=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='QuizContributor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accuracy', models.DecimalField(decimal_places=7, max_digits=8, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('status', models.CharField(blank=True, default='in progress', max_length=255)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('contributor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quizzes.Quiz')),
            ],
        ),
        migrations.AddField(
            model_name='quiz',
            name='contributors',
            field=models.ManyToManyField(related_name='answered_quizzes', through='quizzes.QuizContributor', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='quiz',
            name='founder',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='founded_quizzes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='quiz',
            name='quiz_target',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='targets.Target'),
        ),
        migrations.AddField(
            model_name='quiz',
            name='quiz_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='quizzes.QuestionType'),
        ),
        migrations.AddField(
            model_name='quiz',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='tagged_quizzes', to='tags.Tag'),
        ),
        migrations.AddField(
            model_name='question',
            name='quiz',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quizzes.Quiz'),
        ),
        migrations.AddField(
            model_name='answer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quizzes.Question'),
        ),
        migrations.AddField(
            model_name='answer',
            name='quiz_contributor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='quizzes.QuizContributor'),
        ),
    ]
