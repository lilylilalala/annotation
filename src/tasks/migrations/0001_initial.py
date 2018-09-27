# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-10 14:10
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('copy', models.IntegerField(blank=True, null=True)),
                ('file_path', models.CharField(max_length=255)),
                ('label', models.CharField(blank=True, max_length=255)),
                ('type', models.CharField(blank=True, choices=[(0, 'Contribute'), (1, 'Check')], max_length=128)),
                ('created', models.DateTimeField(null=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('contributor', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='projects.Project')),
            ],
        ),
    ]
