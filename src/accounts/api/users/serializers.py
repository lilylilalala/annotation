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
            'full_name',
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
            'gender',
            'birthday',
            'phone_number',
            'notes',
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
            'full_name',
            'staff',
            'admin',
            'user_type',
            'timestamp',
            'uri',
        ]
        read_only_fields = ['email', 'staff',  'admin', 'user_type', 'full_name']

    def get_uri(self, obj):
        request = self.context.get('request')
        return api_reverse('api-users:detail', kwargs={'id': obj.id}, request=request)


class UserPasswordUpdateSerializer(serializers.ModelSerializer):
    former_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = [
            'former_password',
            'password',
            'password2',
        ]

    def validate_former_password(self, value):
        request = self.context.get('request')
        user_id = request.user.id
        user_obj = User.objects.get(id=user_id)
        if not user_obj.check_password(value):
            raise serializers.ValidationError("Former password is wrong")
        return value

    def validate(self, data):
        pw = data.get('password')
        pw2 = data.pop('password2')
        if pw != pw2:
            raise serializers.ValidationError("Passwords must match")
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        user_id = request.user.id
        user_obj = User.objects.get(id=user_id)
        user_obj.set_password(validated_data.get('password'))
        user_obj.is_active = True
        user_obj.save()
        return user_obj
