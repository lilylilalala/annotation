import os
import re

from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save
from django.contrib.auth import get_user_model
from django.core.files.storage import FileSystemStorage
from django.core.validators import MinValueValidator, MaxValueValidator

from annotation.utils import get_filename_ext, random_string_generator
from targets.models import Target, TargetType
from tags.models import Tag
from quizzes.models import Quiz, QuestionType


User = get_user_model()


def upload_project_file_path(instance, filename):
    name, ext = get_filename_ext(filename)
    while True:
        new_filename = random_string_generator()
        if new_filename not in os.listdir(settings.MEDIA_ROOT):
            break
    final_filename = '{new_filename}{ext}'.format(new_filename=new_filename, ext=ext)
    return final_filename


class Status(models.Model):
    id = models.IntegerField()
    project_status = models.CharField(max_length=128, primary_key=True)
    project_status_name = models.CharField(max_length=128)
    verify_status = models.CharField(max_length=128)
    verify_status_name = models.CharField(max_length=128)

    def __str__(self):
        return str(self.project_status)


class Project(models.Model):
    name = models.CharField(max_length=128, default='unnamed_project')
    tags = models.ManyToManyField(Tag, blank=True, related_name='tagged_projects')
    project_type = models.ForeignKey(QuestionType, related_name='related_projects')
    founder = models.ForeignKey(User, related_name='founded_projects')
    contributors_char = models.CharField(max_length=255, blank=True, default='')
    contributors = models.ManyToManyField(User, blank=True, related_name='contributed_projects')
    inspector = models.ForeignKey(User, blank=True, null=True, related_name='inspected_projects')
    quiz = models.ForeignKey(Quiz, blank=True, null=True, related_name='related_projects')
    accuracy_requirement = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    repetition_rate = models.DecimalField(
        max_digits=2, decimal_places=1, default=1.0,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    description = models.TextField(blank=True)
    verify_staff = models.ForeignKey(User, blank=True, null=True, related_name='verified_projects')
    status = models.ForeignKey(Status, default='unreleased')
    private = models.BooleanField(default=False)
    deadline = models.DateTimeField(blank=True, null=True)
    project_target = models.ForeignKey(Target)
    project_file = models.FileField(
        upload_to=upload_project_file_path,
        storage=FileSystemStorage(location=settings.MEDIA_ROOT),
        blank=True,
        null=True,
    )
    is_file_changed = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    result_file = models.FileField(
        storage=FileSystemStorage(location=settings.RESULT_ROOT, base_url=settings.RESULT_URL),
        blank=True,
        null=True,
    )

    def __str__(self):
        return str(self.id) + '_' + str(self.project_type)

    @property
    def owner(self):
        return self.founder

    @property
    def is_private(self):
        return self.private

    @property
    def quantity(self):
        return self.task_set.count()

    @property
    def copies(self):
        return self.contribution_set.count()

    @property
    def project_status(self):
        return self.status.project_status

    @property
    def verify_status(self):
        return self.status.verify_status

    @property
    def progress(self):
        if self.copies != 0:
            total = self.copies
            completed = self.contribution_set.filter(submitted=True).count()
            return '%d%%' % (completed/total*100)
        return '0%'

    def update_contributors(self):
        for contributor in self.contributors.all():
            self.contributors.remove(contributor)
        contributors_list = re.findall('\d+', self.contributors_char)
        for contributor in contributors_list:
            contributor = User.objects.get(id=int(contributor))
            self.contributors.add(contributor)


@receiver(post_save, sender=Project)
def project_updated_receiver(sender, instance, *args, **kwargs):
    instance.update_contributors()


