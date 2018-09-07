import os
import zipfile
import random

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save

from projects.models import Project
from annotation.utils import get_filename_ext, random_string_generator
import csv

User = get_user_model()

ANSWER_TYPE = (
    (0, 'Contribute'),
    (1, 'Check'),
)


class Task(models.Model):
    project = models.ForeignKey(Project)
    # text_file = models.FileField(
    #     upload_to=upload_file_path,
    #     storage=FileSystemStorage(location=settings.MEDIA_ROOT),
    # )
    copy = models.IntegerField(blank=True, null=True)
    file_path = models.CharField(max_length=255)
    label = models.CharField(max_length=255, blank=True)
    contributor = models.ForeignKey(User, blank=True, null=True, default=None)
    type = models.CharField(max_length=128, blank=True, choices=ANSWER_TYPE)
    created = models.DateTimeField(null=True)
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
    rr = instance.repetition_rate
    length = 0

    if ext == '.zip':
        zf = zipfile.ZipFile(project_file_path, 'r')
        zf.extractall(path=project_file_dir)
        inner_dir_name = os.listdir(project_file_dir)[0]
        project_file_path = os.path.join(project_file_dir, inner_dir_name)
        final_project_file_path = project_file_path.encode('cp437').decode('gbk')
        os.rename(project_file_path, final_project_file_path)
        file_name_list = os.listdir(final_project_file_path)

        for i, file_name in enumerate(file_name_list):
            for j in range(int(rr)):
                Task.objects.create(
                    project=instance,
                    file_path=os.path.join(final_project_file_path, file_name),
                    copy=i,
                    type=0,
                )
        length = i + 1

    elif ext == '.csv':
        inner_dir_name = '%s' % instance.name
        project_file_dir = os.path.join(project_file_dir, inner_dir_name)
        os.mkdir(project_file_dir)
        reader = csv.DictReader(open(project_file_path, encoding='utf-8'))

        for i, row in enumerate(reader):
            for j in range(int(rr)):
                file_name = '%s.csv' % row['\ufeffid']
                final_project_file_path = os.path.join(project_file_dir, file_name)
                f = open(final_project_file_path, 'w', newline='', encoding='utf-8')
                writer = csv.DictWriter(f, dialect='excel', fieldnames=reader.fieldnames)
                writer.writeheader()
                writer.writerow(row)
                Task.objects.create(
                    project=instance,
                    file_path=final_project_file_path,
                    copy=i,
                    type=0,
                )
        length = i + 1

    if 1 < rr < 2:
        num = int((rr - 1) * length)
        rand_list = random.sample(range(length), num)
        for k in rand_list:
            task = Task.objects.get(project=instance, copy=k)
            task.id = None
            task.save()



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


@receiver(post_save, sender=Task)
def task_updated_receiver(sender, instance, *args, **kwargs):
    project = instance.project
    Project.objects.filter(id=project.id).update(status=project.project_status)
