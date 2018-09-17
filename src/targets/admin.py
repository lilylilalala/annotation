from django.contrib import admin

from .models import Target, TargetType


admin.site.register(Target)

admin.site.register(TargetType)
