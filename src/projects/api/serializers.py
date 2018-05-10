from rest_framework import serializers
from rest_framework.reverse import reverse as api_reverse

from projects.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    uri = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'project_type',
            'founder',
            'contributors',
            'description',
            'verify_status',
            'verify_staff',
            'project_file',
            'uri',
        ]
        read_only_fields = ['founder']

    def get_uri(self, obj):
        request = self.context.get('request')
        return api_reverse('api-projects:detail', kwargs={'id': obj.id}, request=request)


class ProjectInlineUserSerializer(ProjectSerializer):
    class Meta:
        model = Project
        fields = [
            'id',
            'project_type',
            'founder',
            'contributors',
            'description',
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
            'verify_status',
            'project_file',
            'uri',
        ]
        read_only_fields = ['project_type', 'founder', 'description', 'project_file']
