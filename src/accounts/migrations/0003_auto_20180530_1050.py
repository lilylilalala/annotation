# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-30 10:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20180502_1633'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('ordinary_user', '普通用户'), ('staff', '员工'), ('administrator', '管理员')], default='ordinary_user', max_length=255),
        ),
    ]