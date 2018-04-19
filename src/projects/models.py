from django.db import models
from django.contrib.auth import get_user_model


PROJECT_TYPE = (
    ('TextClassification', '文本分类'),
    ('ImageClassification', '图像分类'),
)


User = get_user_model()


class Project(models.Model):
    project_type = models.CharField(max_length=128, choices=PROJECT_TYPE)
    founder = models.ForeignKey(User, related_name='founded_projects')
    contributors = models.ManyToManyField(User, blank=True, related_name='contributed_projects')
    description = models.TextField(blank=True)
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id) + '_' + self.project_type

    @property
    def owner(self):
        return self.founder
