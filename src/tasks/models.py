import os
import zipfile
import random

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from django.core.files.storage import FileSystemStorage

from projects.models import Project
from annotation.utils import get_filename_ext, random_string_generator
import csv

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

    @property
    def contributor_name(self):
        if self.contributor:
            return self.contributor.full_name
        else:
            return None


def create_tasks(instance):
    name, ext = get_filename_ext(instance.project_file.name)
    project_file_path = os.path.join(settings.MEDIA_ROOT, instance.project_file.name)
    project_file_dir = os.path.join(settings.MEDIA_ROOT, name)
    os.mkdir(project_file_dir)

    if ext == '.zip':
        zf = zipfile.ZipFile(project_file_path, 'r')
        zf.extractall(path=project_file_dir)
        inner_dir_name = os.listdir(project_file_dir)[0]
        final_project_file_path = os.path.join(project_file_dir, inner_dir_name)
        file_name_list = os.listdir(final_project_file_path)

        for file_name in file_name_list:
            Task.objects.create(
                project=instance,
                file_path=os.path.join(final_project_file_path, file_name),
            )

    elif ext == '.csv':
        inner_dir_name = '%s' % instance.name
        project_file_dir = os.path.join(project_file_dir, inner_dir_name)
        os.mkdir(project_file_dir)
        reader = csv.DictReader(open(project_file_path, encoding='utf-8'))

        for row in reader:
            file_name = '%s.csv' % row['id']
            final_project_file_path = os.path.join(project_file_dir, file_name)
            f = open(final_project_file_path, 'w', newline='')
            writer = csv.writer(f, dialect='excel')
            writer.writerow([row['text']])
            Task.objects.create(
                project=instance,
                file_path=final_project_file_path,
            )


@receiver(pre_save, sender=Project)
def project_file_pre_receiver(sender, instance, **kwargs):
    try:
        obj = Project.objects.get(id=instance.id)
        if instance.project_file and (not instance.project_file.name == obj.project_file.name):
            obj.task_set.all().delete()
            instance.is_file_changed = True
        else:
            instance.is_file_changed = False
            instance.project_file = obj.project_file
    except:
        pass


@receiver(post_save, sender=Project)
def project_file_post_receiver(sender, instance, created, *args, **kwargs):
    if (instance.is_file_changed or created) and instance.project_file:
        create_tasks(instance)


@receiver(pre_save, sender=Task)
def task_updated_receiver(sender, instance, *args, **kwargs):
    project = instance.project
    Project.objects.filter(id=project.id).update(status=project.project_status)
