import csv

from rest_framework import serializers

from tasks.models import Task, Contribution, Inspection
from targets.api.serializers import TargetSerializer
from annotation.utils import get_filename_ext


class TaskContributeSerializer(serializers.ModelSerializer):
    project_type = serializers.SerializerMethodField(read_only=True)
    target = serializers.SerializerMethodField(read_only=True)
    text_content = serializers.SerializerMethodField(read_only=True)
    contributor_name = serializers.SerializerMethodField(read_only=True)
    previous_id = serializers.SerializerMethodField(read_only=True)
    next_id = serializers.SerializerMethodField(read_only=True)
    contribution_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Contribution
        fields = [
            'id',
            'project_type',
            'target',
            'text_content',
            'contributor',
            'contributor_name',
            'created',
            'updated',
            'previous_id',
            'next_id',
            'contribution_id',
            'submitted',
            'label',
        ]
        read_only_fields = ['id', 'contributor', 'created']

    def get_project_type(self, obj):
        return obj.project.project_type.name

    def get_target(self, obj):
        target = obj.project.project_target
        return TargetSerializer(target).data

    def get_text_content(self, obj):
        path = obj.task.file_path
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
        if obj.contributor:
            return obj.contributor.full_name
        return None

    def get_previous_id(self, obj):
        if obj.contributor:
            my_tasks = Contribution.objects.filter(project=obj.project, contributor=obj.contributor)
            previous = my_tasks.filter(created__lt=obj.created).order_by('-created').first()
            if previous:
                return previous.id
        return None

    def get_next_id(self, obj):
        if obj.contributor:
            my_tasks = Contribution.objects.filter(project=obj.project, contributor=obj.contributor)
            next_task = my_tasks.filter(created__gt=obj.created).order_by('created').first()
            if next_task:
                return next_task.id
        return None


class TaskContributeUpdateSerializer(TaskContributeSerializer):
    class Meta:
        model = Contribution
        fields = [
            'id',
            'project_type',
            'target',
            'text_content',
            'contributor',
            'contributor_name',
            'created',
            'updated',
            'previous_id',
            'next_id',
            'submitted',
            'label',
        ]
        read_only_fields = ['id', 'contributor', 'created', 'submitted']


class TaskInspectSerializer(serializers.ModelSerializer):
    project_type = serializers.SerializerMethodField(read_only=True)
    target = serializers.SerializerMethodField(read_only=True)
    text_content = serializers.SerializerMethodField(read_only=True)
    inspector_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Inspection
        fields = [
            'id',
            'project_type',
            'target',
            'text_content',
            'label',
            'inspector',
            'inspector_name',
            'submitted',
            'created',
            'updated',
        ]
        read_only_fields = ['id', 'inspector', 'created']

    def get_project_type(self, obj):
        return obj.task.project.project_type.name

    def get_target(self, obj):
        target = obj.task.project.project_target
        return TargetSerializer(target).data

    def get_text_content(self, obj):
        path = obj.task.file_path
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

    def get_inspector_name(self, obj):
        try:
            return obj.inspector.full_name
        except:
            return None


class ContributeResultSerializer(TaskContributeSerializer):
    class Meta:
        model = Contribution
        fields = [
            'id',
            'label',
            'contributor',
            'contributor_name',
            'created',
            'updated',
        ]
        read_only_fields = ['created', 'label']


class InspectResultSerializer(TaskInspectSerializer):
    class Meta:
        model = Inspection
        fields = [
            'id',
            'label',
            'inspector',
            'inspector_name',
            'created',
            'updated',
        ]
        read_only_fields = ['created', 'label']


class TaskResultSerializer(serializers.ModelSerializer):
    text_content = serializers.SerializerMethodField(read_only=True)
    inspection = serializers.SerializerMethodField(read_only=True)
    contribution = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Task
        fields = [
            'id',
            'text_content',
            'label',
            'updated',
            'inspection',
            'contribution',
        ]

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

    def get_inspection(self, obj):
        try:
            return InspectResultSerializer(obj.inspection).data
        except:
            return None

    def get_contribution(self, obj):
        return ContributeResultSerializer(obj.contribution_set, many=True).data
