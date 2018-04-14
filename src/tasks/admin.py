from django.contrib import admin
from .models import TextClassification, ImageClassification


admin.site.register(TextClassification)
admin.site.register(ImageClassification)
