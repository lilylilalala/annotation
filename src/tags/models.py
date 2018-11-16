from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


TAG_TYPE = (
    (1, '一级'),
    (2, '二级'),
)


class Tag(models.Model):
    name = models.CharField(max_length=128, unique=True)
    parent = models.ForeignKey('self', null=True, related_name='child_tags')
    level = models.IntegerField(choices=TAG_TYPE, default=1)
    description = models.TextField(blank=True)
    updated = models.DateTimeField(auto_now=True)
    founder = models.ForeignKey(User, related_name='founded_tags')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id) + '_' + self.name

    @property
    def editable(self):
        tag_quiz = self.tagged_quizzes.all()
        if tag_quiz:
            return False
        tag_project = self.tagged_projects.all()
        if tag_project:
            return False
        return True

    @property
    def deletable(self):
        tag_quiz = self.tagged_quizzes.all()
        if tag_quiz:
            return False
        tag_project = self.tagged_projects.all()
        if tag_project:
            return False
        child = Tag.objects.filter(parent=self.id)
        if child:
            return False
        return True
