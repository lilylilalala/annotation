from rest_framework import serializers
from rest_framework.reverse import reverse as api_reverse

from tags.models import Tag


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
            'parent',
            'level',
            'description',
            'founder',
            'updated',
        ]
        read_only_fields = ['updated', 'founder']
