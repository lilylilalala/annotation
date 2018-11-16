from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class TargetType(models.Model):
    name = models.CharField(max_length=128, unique=True)
    chinese_name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return str(self.name)


class Target(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=255, unique=True)
    type = models.ForeignKey(TargetType, related_name='related_targets')
    entity = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user) + '_' + str(self.name)

    @property
    def owner(self):
        return self.user

    @property
    def editable(self):
        target_quiz = self.target_quizzes.all()
        if target_quiz:
            return False
        target_project = self.target_projects.all()
        if target_project:
            return False
        return True

    @property
    def deletable(self):
        target_quiz = self.target_quizzes.all()
        if target_quiz:
            return False
        target_project = self.target_projects.all()
        if target_project:
            return False
        return True
