# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-04 10:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0009_project_completed_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='completed_status',
            field=models.NullBooleanField(default=None),
        ),
    ]
