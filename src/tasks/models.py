import os
import zipfile
import random
from collections import Counter

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save

from projects.models import Project, Status
from annotation.utils import get_filename_ext, random_string_generator
import csv

User = get_user_model()


class Task(models.Model):
    project = models.ForeignKey(Project)
    copy = models.IntegerField(blank=True, null=True)
    file_path = models.CharField(max_length=255)
    label = models.CharField(max_length=255, blank=True)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.project) + '_' + str(self.id)

    @property
    def is_done(self):
        if self.contribution_set.filter(label=''):
            return False
        return True


class Contribution(models.Model):
    project = models.ForeignKey(Project)
    task = models.ForeignKey(Task)
    label = models.CharField(max_length=255, blank=True)
    contributor = models.ForeignKey(User, blank=True, null=True)
    created = models.DateTimeField(null=True)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.task) + '_' + str(self.id)


class Inspection(models.Model):
    project = models.ForeignKey(Project)
    task = models.OneToOneField(Task)
    label = models.CharField(max_length=255, blank=True)
    inspector = models.ForeignKey(User, blank=True, null=True)
    created = models.DateTimeField(null=True)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.task) + '_' + str(self.id)


def create_tasks(instance):
    name, ext = get_filename_ext(instance.project_file.name)
    project_file_path = os.path.join(settings.MEDIA_ROOT, instance.project_file.name)
    project_file_dir = os.path.join(settings.MEDIA_ROOT, name)
    os.mkdir(project_file_dir)
    rr = instance.repetition_rate

    if ext == '.zip':
        zf = zipfile.ZipFile(project_file_path, 'r')
        zf.extractall(path=project_file_dir)
        inner_dir_name = os.listdir(project_file_dir)[0]
        project_file_path = os.path.join(project_file_dir, inner_dir_name)
        final_project_file_path = project_file_path.encode('cp437').decode('gbk')
        os.rename(project_file_path, final_project_file_path)
        file_name_list = os.listdir(final_project_file_path)

        for file_name in file_name_list:
            Task.objects.create(
                project=instance,
                file_path=os.path.join(final_project_file_path, file_name),
                copy=int(rr),
            )

    elif ext == '.csv':
        inner_dir_name = '%s' % instance.name
        project_file_dir = os.path.join(project_file_dir, inner_dir_name)
        os.mkdir(project_file_dir)
        reader = csv.DictReader(open(project_file_path, encoding='utf-8'))

        for row in reader:
            file_name = '%s.csv' % row['\ufeffid']
            final_project_file_path = os.path.join(project_file_dir, file_name)
            f = open(final_project_file_path, 'w', newline='', encoding='utf-8')
            writer = csv.DictWriter(f, dialect='excel', fieldnames=reader.fieldnames)
            writer.writeheader()
            writer.writerow(row)
            Task.objects.create(
                project=instance,
                file_path=final_project_file_path,
                copy=int(rr),
            )

    if 1 < rr < 2:
        length = instance.task_set.count()
        num = int((rr - 1) * length)
        ids = instance.task_set.values_list("id", flat=True)
        rand_list = random.sample(set(ids), num)
        for i in rand_list:
            Task.objects.filter(id=i).update(copy=2)

    for task in Task.objects.filter(project=instance):
        for copy in range(task.copy):
            Contribution.objects.create(project=instance, task=task)


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


@receiver(post_save, sender=Contribution)
def contribution_updated_receiver(sender, instance, *args, **kwargs):
    task = instance.task
    if task.is_done:
        labels = task.contribution_set.values_list('label', flat=True)
        if len(set(labels)) == 1:
            task.label = instance.label
        else:
            top_labels = Counter(labels).most_common(2)
            if top_labels[0][1] != top_labels[1][1]:
                task.label = top_labels[0][0]
            else:
                Inspection.objects.create(task=task, project=instance.project)
        task.save()


@receiver(post_save, sender=Inspection)
def inspection_updated_receiver(sender, instance, *args, **kwargs):
    task = instance.task
    if instance.label:
        task.label = instance.label
        task.save()


@receiver(post_save, sender=Task)
def task_updated_receiver(sender, instance, *args, **kwargs):
    project = instance.project
    if project.progress == '100%':
        if project.task_set.filter(label=''):
            Project.objects.filter(id=project.id).update(status='checking')
        else:
            project.status = Status(pk='completed')
            project.save()



