from rest_framework import serializers

from tasks.models import Task
from annotation.utils import get_filename_ext
import csv

SWITCH_TYPE = (
    ('former', '上一题'),
    ('next', '下一题'),
)


class TaskSerializer(serializers.ModelSerializer):
    # text_file_path = serializers.SerializerMethodField(read_only=True)
    project_type = serializers.SerializerMethodField(read_only=True)
    target = serializers.SerializerMethodField(read_only=True)
    target_name = serializers.SerializerMethodField(read_only=True)
    target_entity = serializers.SerializerMethodField(read_only=True)
    target_description = serializers.SerializerMethodField(read_only=True)
    text_content = serializers.SerializerMethodField(read_only=True)
    contributor_name = serializers.SerializerMethodField(read_only=True)
    previous_id = serializers.SerializerMethodField(read_only=True)
    next_id = serializers.SerializerMethodField(read_only=True)

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
            'created',
            'updated',
            'previous_id',
            'next_id',
        ]
        read_only_fields = ['id', 'project', 'contributor', 'created', 'previous_id', 'next_id']

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
        name, ext = get_filename_ext(path)
        if ext == '.csv':
            reader = csv.DictReader(open(path, encoding='utf-8'))
            for i, row in enumerate(reader):
                if i == 0:
                    content = row
        else:
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
        return content

    def get_contributor_name(self, obj):
        return obj.contributor_name

    def get_previous_id(self, obj):
        my_tasks = Task.objects.filter(project=obj.project, contributor=obj.contributor)
        try:
            previous = my_tasks.filter(created__lt=obj.created).order_by('-created').first()
            return previous.id
        except:
            return None

    def get_next_id(self, obj):
        my_tasks = Task.objects.filter(project=obj.project, contributor=obj.contributor)
        try:
            next_task = my_tasks.filter(created__gt=obj.created).order_by('created').first()
            return next_task.id
        except:
            return None


class TaskResultSerializer(TaskSerializer):
    class Meta:
        model = Task
        fields = [
            'id',
            'project',
            'project_type',
            'text_content',
            'label',
            'contributor',
            'contributor_name',
            'created',
            'updated',
        ]
