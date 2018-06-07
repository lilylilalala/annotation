import os

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.storage import FileSystemStorage

from annotation.utils import get_filename_ext, random_string_generator


User = get_user_model()


PROJECT_TYPE = (
    ('TextClassification', '文本分类'),
    ('ImageClassification', '图像分类'),
    ('KeywordRecognition', '关键词识别'),
    ('EntityRecognition', '实体识别'),
)

VERIFY_STATUS_TYPE = (
    ('verifying', '审核中'),
    ('verification succeed', '审核通过'),
    ('verification failed', '审核未通过'),
)


def upload_project_file_path(instance, filename):
    name, ext = get_filename_ext(filename)
    while True:
        new_filename = random_string_generator()
        if new_filename not in os.listdir(settings.MEDIA_ROOT):
            break
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return final_filename


class Project(models.Model):
    project_type = models.CharField(max_length=128, choices=PROJECT_TYPE)
    founder = models.ForeignKey(User, related_name='founded_projects')
    contributors = models.ManyToManyField(User, blank=True, related_name='contributed_projects')
    description = models.TextField(blank=True)
    verify_status = models.CharField(max_length=255, default='verifying', choices=VERIFY_STATUS_TYPE)
    verify_staff = models.ForeignKey(User, blank=True, null=True, related_name='verified_projects')
    private = models.BooleanField(default=False)
    deadline = models.DateTimeField(blank=True, null=True)
    project_target = models.CharField(max_length=255, blank=True)
    project_file = models.FileField(
        upload_to=upload_project_file_path,
        storage=FileSystemStorage(location=settings.MEDIA_ROOT),
        blank=True,
        null=True,
    )
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id) + '_' + self.project_type

    @property
    def owner(self):
        return self.founder

    @property
    def is_private(self):
        return self.private

    @property
    def is_completed(self):
        if self.task_set.all().filter(label=''):
            return False
        return True
