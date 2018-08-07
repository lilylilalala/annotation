from rest_framework import serializers

from tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    # text_file_path = serializers.SerializerMethodField(read_only=True)
    text_content = serializers.SerializerMethodField(read_only=True)
    contributor_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'project',
            'text_content',
            'label',
            'contributor',
            'contributor_name',
            'updated',
        ]
        read_only_fields = ['id', 'project', 'contributor']

    # def get_file_path(self, obj):
    #     return obj.text_file.url

    def get_text_content(self, obj):
        path = obj.file_path
        with open(path, 'r', encoding='utf-8') as file:
            text_content = file.read().strip()
        return text_content

    def get_contributor_name(self, obj):
        return obj.contributor_name

