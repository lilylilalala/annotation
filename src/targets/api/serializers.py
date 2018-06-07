from rest_framework import serializers

from targets.models import Target


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = [
            'id',
            'user',
            'name',
            'type',
            'entity',
            'description',
        ]
        read_only_fields = ['user']
