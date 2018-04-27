from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.reverse import reverse as api_reverse

from projects.api.serializers import ProjectInlineUserSerializer


User = get_user_model()


class UserDetailSerializer(serializers.ModelSerializer):
    uri = serializers.SerializerMethodField(read_only=True)
    project = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'uri',
            'project',
        ]

    def get_uri(self, obj):
        request = self.context.get('request')
        return api_reverse('api-users:detail', kwargs={'id': obj.id}, request=request)

    def get_project(self, obj):
        request = self.context.get('request')
        limit = 10
        if request:
            limit_query = request.GET.get('limit')
            try:
                limit = int(limit_query)
            except:
                pass
        founded_qs = obj.founded_projects.all().order_by('-timestamp')
        contributed_qs = obj.contributed_projects.all().order_by('-timestamp')
        data = {
            'founded_projects': ProjectInlineUserSerializer(
                founded_qs[:limit], context={'request': request}, many=True).data,
            'contributed_projects': ProjectInlineUserSerializer(
                contributed_qs[:limit], context={'request': request}, many=True).data,
        }
        return data


class UserDetailUpdateSerializer(serializers.ModelSerializer):
    uri = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'full_name',
            'phone_number',
            'uri',
        ]

    def get_uri(self, obj):
        request = self.context.get('request')
        return api_reverse('api-users:detail', kwargs={'id': obj.id}, request=request)


class UserInlineSerializer(serializers.ModelSerializer):
    uri = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'uri',
        ]
        read_only_fields = ['email']

    def get_uri(self, obj):
        request = self.context.get('request')
        return api_reverse('api-users:detail', kwargs={'id': obj.id}, request=request)
