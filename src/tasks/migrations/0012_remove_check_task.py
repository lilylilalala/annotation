# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-13 13:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0011_auto_20180913_1350'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='check',
            name='task',
        ),
    ]
