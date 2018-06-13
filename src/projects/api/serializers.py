from rest_framework import serializers
from rest_framework.reverse import reverse as api_reverse

from projects.models import Project
from targets.api.serializers import TargetSerializer


PROJECT_TYPE = {
    'TextClassification': '文本分类',
    'ImageClassification': '图像分类',
    'KeywordRecognition': '关键词识别',
    'EntityRecognition': '实体识别',
}


class ProjectSerializer(serializers.ModelSerializer):
    uri = serializers.SerializerMethodField(read_only=True)
    project_type_name = serializers.SerializerMethodField(read_only=True)
    is_completed = serializers.SerializerMethodField(read_only=True)
    target = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'project_type',
            'project_type_name',
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

    def get_project_type_name(self, obj):
        return PROJECT_TYPE[obj.project_type]

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
            'project_type_name',
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
            'project_type_name',
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
