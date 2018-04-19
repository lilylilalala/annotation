import os
import random

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.storage import FileSystemStorage

from projects.models import Project
from annotation.utils import get_filename_ext, random_string_generator

User = get_user_model()


TEXT_CLASSIFICATION_LABEL_TYPE = (
    ('政治', 'political'),
    ('体育', 'sport'),
)


def upload_text_file_path(instance, filename):
    name, ext = get_filename_ext(filename)
    new_filename = random_string_generator()
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return '{project_id}/{final_filename}'.format(
        project_id=instance.project.id,
        final_filename=final_filename
    )


class TextClassification(models.Model):
    project = models.ForeignKey(Project)
    text_file = models.FileField(
        upload_to=upload_text_file_path,
        storage=FileSystemStorage(location=settings.MEDIA_ROOT),
    )
    label = models.CharField(max_length=128, blank=True, choices=TEXT_CLASSIFICATION_LABEL_TYPE)
    contributor = models.ForeignKey(User, blank=True, null=True, default=None)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.project) + '_' + str(self.id)


def upload_image_file_path(instance, filename):
    new_filename = random.randint(1, 9999999999)
    name, ext = get_filename_ext(filename)
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return 'image_classification/{new_filename}/{final_filename}'.format(
        new_filename=new_filename,
        final_filename=final_filename
    )


IMAGE_CLASSIFICATION_LABEL_TYPE = (
    ('猫', 'cat'),
    ('狗', 'dog'),
)


class ImageClassification(models.Model):
    project = models.ForeignKey(Project)
    image_file = models.ImageField(upload_to=upload_image_file_path, null=True, blank=True)
    label = models.CharField(max_length=128, blank=True, choices=IMAGE_CLASSIFICATION_LABEL_TYPE)
    contributor = models.ForeignKey(User, blank=True, null=True, default=None)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.project) + '_' + str(self.id)
