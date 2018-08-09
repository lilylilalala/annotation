from rest_framework import serializers

from tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    # text_file_path = serializers.SerializerMethodField(read_only=True)
    project_type = serializers.SerializerMethodField(read_only=True)
    target = serializers.SerializerMethodField(read_only=True)
    target_name = serializers.SerializerMethodField(read_only=True)
    target_entity = serializers.SerializerMethodField(read_only=True)
    target_description = serializers.SerializerMethodField(read_only=True)
    text_content = serializers.SerializerMethodField(read_only=True)
    contributor_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'project',
            'project_type',
            'target',
            'target_name',
            'target_entity',
            'target_description',
            'text_content',
            'label',
            'contributor',
            'contributor_name',
            'updated',
        ]
        read_only_fields = ['id', 'project', 'contributor']

    # def get_file_path(self, obj):
    #     return obj.text_file.url

    def get_project_type(self, obj):
        return obj.project.project_type

    def get_target(self, obj):
        return obj.project.project_target.id

    def get_target_name(self, obj):
        return obj.project.project_target.name

    def get_target_entity(self, obj):
        return obj.project.project_target.entity

    def get_target_description(self, obj):
        return obj.project.project_target.description

    def get_text_content(self, obj):
        path = obj.file_path
        with open(path, 'r', encoding='utf-8') as file:
            text_content = file.read().strip()
        return text_content

    def get_contributor_name(self, obj):
        return obj.contributor_name

