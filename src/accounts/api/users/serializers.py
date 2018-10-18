from django.contrib.auth import get_user_model
from django.db.models import Sum

from rest_framework import serializers
from rest_framework.reverse import reverse as api_reverse

from grades.models import Grade
from tags.models import Tag

User = get_user_model()


class UserDetailSerializer(serializers.ModelSerializer):
    grade = serializers.SerializerMethodField(read_only=True)
    uri = serializers.SerializerMethodField(read_only=True)
    founded_projects = serializers.SerializerMethodField(read_only=True)
    contributed_projects = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'full_name',
            'grade',
            'uri',
            'founded_projects',
            'contributed_projects',
        ]

    def get_grade(self, obj):
        grade_dict = {}
        grade_set = Grade.objects.filter(user=obj)
        tags = set(grade_set.values_list('tag', flat=True))
        for tag in tags:
            total_good = grade_set.filter(tag=tag).aggregate(Sum('good_labels'))['good_labels__sum']
            total = grade_set.filter(tag=tag).aggregate(Sum('labels'))['labels__sum']
            grade_dict[Tag.objects.get(id=tag).name] = total_good/total
        return grade_dict

    def get_uri(self, obj):
        request = self.context.get('request')
        return api_reverse('api-users:detail', kwargs={'id': obj.id}, request=request)

    def get_founded_projects(self, obj):
        return obj.founded_projects.values_list('id', flat=True)

    def get_contributed_projects(self, obj):
        return obj.contributed_projects.values_list('id', flat=True)


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


class EditContributorsSerializer(UserDetailSerializer):
    user_id = serializers.CharField()

    class Meta:
        model = User
        fields = [
            'user_id',
            'email',
            'full_name',
            'grade',
            'uri',
        ]
        read_only_fields = ['email', 'full_name']


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
