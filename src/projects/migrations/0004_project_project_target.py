# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-05 10:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_auto_20180530_1050'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='project_target',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]