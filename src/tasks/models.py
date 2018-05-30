import os
import zipfile
import random

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.core.files.storage import FileSystemStorage

from projects.models import Project
from annotation.utils import get_filename_ext, random_string_generator


User = get_user_model()


# def upload_file_path(instance, filename):
#     name, ext = get_filename_ext(filename)
#     new_filename = random_string_generator()
#     final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
#     return '{project_id}/{final_filename}'.format(
#         project_id=instance.project.id,
#         final_filename=final_filename
#     )


class Task(models.Model):
    project = models.ForeignKey(Project)
    # text_file = models.FileField(
    #     upload_to=upload_file_path,
    #     storage=FileSystemStorage(location=settings.MEDIA_ROOT),
    # )
    file_path = models.CharField(max_length=255)
    label = models.CharField(max_length=255, blank=True)
    contributor = models.ForeignKey(User, blank=True, null=True, default=None)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.project) + '_' + str(self.id)


def project_created_receiver(sender, instance, created, *args, **kwargs):
    if created and instance.project_file:
        project_file_path = os.path.join(settings.MEDIA_ROOT, instance.project_file.name)
        name, ext = get_filename_ext(instance.project_file.name)
        project_file_dir = os.path.join(settings.MEDIA_ROOT, name)
        os.mkdir(project_file_dir)
        zf = zipfile.ZipFile(project_file_path, 'r')
        zf.extractall(path=project_file_dir)
        # os.remove(project_file_path)

        inner_dir_name = os.listdir(project_file_dir)[0]
        finally_project_file_path = os.path.join(project_file_dir, inner_dir_name)
        file_name_list = os.listdir(finally_project_file_path)
        for file_name in file_name_list:
            Task.objects.create(
                project=instance,
                file_path=os.path.join(finally_project_file_path, file_name),
            )


post_save.connect(project_created_receiver, sender=Project)
