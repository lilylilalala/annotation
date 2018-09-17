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
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id) + '_Project' + str(self.project.id) + '_' + self.user.full_name + '_' + self.tag.name


@receiver(post_save, sender=Project)
def receiver(sender, instance, *args, **kwargs):    
    if instance.project_status == 'completed':
        old_grade_set = Grade.objects.filter(project=instance)
        if old_grade_set:
            old_grade_set.delete()
        contribution_set = instance.contribution_set.all()
        contributors = set(contribution_set.values_list('contributor', flat=True))
        for user in contributors:
            user_done_set = contribution_set.filter(contributor=user)
            labels = user_done_set.count()
            good_labels = 0
            for contribution in user_done_set:
                if contribution.label == contribution.task.label:
                    good_labels += 1

            for tag in instance.tags.all():
                Grade.objects.create(project=instance,
                                     user_id=user,
                                     tag=tag,
                                     labels=labels,
                                     good_labels=good_labels)
