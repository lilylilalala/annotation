from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


TARGET_TYPE = (
    (0, '类目目标'),
    (1, '关键字目标'),
    (2, '实体目标'),
)


class Target(models.Model):
    user = models.ForeignKey(User)
    name = models.CharField(max_length=255, unique=True)
    type = models.CharField(max_length=255, blank=True, choices=TARGET_TYPE)
    entity = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    updated = models.DateTimeField(auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user) + '_' + str(self.name)

    @property
    def owner(self):
        return self.user
