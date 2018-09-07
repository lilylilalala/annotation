from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

from projects.models import Project
from tags.models import Tag


User = get_user_model()


class Grade(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)
    tag = models.ForeignKey(Tag)
    good_labels = models.IntegerField(blank=True, null=True)
    labels = models.IntegerField(blank=True, null=True)
    total_good_labels = models.IntegerField(blank=True, null=True)
    total_labels = models.IntegerField(blank=True, null=True)
    final_grade = models.CharField(max_length=255, blank=True)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.id + '_' + self.user.full_name + '_' + self.tag.name


'''
@receiver(post_save, sender=Project)
def receiver(sender, instance, *args, **kwargs):    
    if instance.is_completed:
        for user in instance.contributors:
            for tag in instance.tags:
                grade = Grade(project=instance, user=user, tag=tag)
'''