from rest_framework import serializers
from rest_framework.reverse import reverse as api_reverse

from projects.models import Project
from targets.api.serializers import TargetSerializer


class ProjectSerializer(serializers.ModelSerializer):
    uri = serializers.SerializerMethodField(read_only=True)
    is_completed = serializers.SerializerMethodField(read_only=True)
    target = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'project_type',
            'founder',
            'contributors',
            'description',
            'private',
            'deadline',
            'is_completed',
            'project_target',
            'target',
            'project_file',
            'uri',
        ]
        read_only_fields = ['founder']

    def get_uri(self, obj):
        request = self.context.get('request')
        return api_reverse('api-projects:detail', kwargs={'id': obj.id}, request=request)

    def get_is_completed(self, obj):
        return obj.is_completed

    def get_target(self, obj):
        target = obj.project_target
        return TargetSerializer(target).data


class ProjectInlineUserSerializer(ProjectSerializer):
    class Meta:
        model = Project
        fields = [
            'id',
            'project_type',
            'founder',
            'contributors',
            'description',
            'deadline',
            'project_target',
            'target',
            'is_completed',
            'uri',
        ]
        read_only_fields = ['project_type', 'founder']


class ProjectInlineVerifySerializer(ProjectSerializer):
    class Meta:
        model = Project
        fields = [
            'id',
            'project_type',
            'founder',
            'description',
            'deadline',
            'verify_status',
            'project_file',
            'uri',
        ]
        read_only_fields = ['project_type', 'founder', 'description', 'project_file']


class ProjectTargetSerializer(ProjectSerializer):
    class Meta:
        model = Project
        fields = [
            'project_target',
        ]
    read_only_fields = ['project_target']
