from rest_framework import serializers

from tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    # text_file_path = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'project',
            'file_path',
            'label',
            'contributor',
        ]
        read_only_fields = ['id', 'project', 'contributor', 'file_path']

    # def get_file_path(self, obj):
    #     return obj.text_file.url
