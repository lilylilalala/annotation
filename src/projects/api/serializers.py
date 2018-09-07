from rest_framework import serializers
from rest_framework.reverse import reverse as api_reverse

from projects.models import Project
from targets.api.serializers import TargetSerializer
from tags.api.serializers import TagBriefSerializer


PROJECT_TYPE = {
    'DataClassification': '数据分类',
    'TextClassification': '文本分类',
    'KeywordRecognition': '关键词识别',
    'EntityRecognition': '实体识别',
}

VERIFY_STATUS_TYPE = (
    ('verification succeed', '审核通过'),
    ('verification failed', '审核未通过'),
)


class ProjectSerializer(serializers.ModelSerializer):
    uri = serializers.SerializerMethodField(read_only=True)
    project_type_name = serializers.SerializerMethodField(read_only=True)
    quiz_name = serializers.SerializerMethodField(read_only=True)
    quantity = serializers.SerializerMethodField(read_only=True)
    project_status = serializers.SerializerMethodField(read_only=True)
    is_completed = serializers.SerializerMethodField(read_only=True)
    progress = serializers.SerializerMethodField(read_only=True)
    tags_detail = serializers.SerializerMethodField(read_only=False)
    target = serializers.SerializerMethodField(read_only=True)
    is_in = serializers.SerializerMethodField(read_only=True)
    my_quantity = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'tags',
            'tags_detail',
            'project_type',
            'project_type_name',
            'founder',
            'contributors',
            'contributors_char',
            'inspector',
            'quiz',
            'quiz_name',
            'accuracy_requirement',
            'repetition_rate',
            'description',
            'verify_status',
            'status',
            'private',
            'deadline',
            'quantity',
            'project_status',
            'is_completed',
            'progress',
            'project_target',
            'target',
            'project_file',
            'is_in',
            'my_quantity',
            'uri',
        ]
        read_only_fields = ['founder', 'verify_status', 'status', 'contributors']

    def validate_tags(self, value):
        if len(value) > 3:
            raise serializers.ValidationError("No more than three tags.")
        return value

    def validate_repetition_rate(self, value):
        if value > 2 and value != int(value):
            raise serializers.ValidationError("Repetition rate should be integer if it is greater than 2.")
        return value

    def validate(self, data):
        quiz = data.get('quiz')
        accuracy_requirement = data.get('accuracy_requirement')
        if not quiz and accuracy_requirement != 0.0:
            raise serializers.ValidationError("Accuracy Requirement should be 0.0 if no quiz.")

        project_type = data.get('project_type')
        repetition_rate = data.get('repetition_rate')
        inspector = data.get('inspector')
        if project_type not in ['DataClassification', 'TextClassification']:
            if inspector or repetition_rate != 1.0:
                raise serializers.ValidationError(
                    "Only Classification projects may have a inspector or a repetition rate unequal to 1.0."
                )
        else:
            if inspector and repetition_rate == 1.0:
                raise serializers.ValidationError(
                    "No need to include a inspector since repetition rate is 1.0."
                )
        return data

    def get_uri(self, obj):
        request = self.context.get('request')
        return api_reverse('api-projects:detail', kwargs={'id': obj.id}, request=request)

    def get_project_type_name(self, obj):
        return PROJECT_TYPE[obj.project_type]

    def get_quiz_name(self, obj):
        if obj.quiz:
            return obj.quiz.name
        else:
            return None

    def get_quantity(self, obj):
        return obj.quantity

    def get_project_status(self, obj):
        return obj.project_status

    def get_is_completed(self, obj):
        return obj.is_completed

    def get_progress(self, obj):
        return obj.progress

    def get_tags_detail(self, obj):
        tags_queryset = obj.tags
        return TagBriefSerializer(tags_queryset, many=True).data

    def get_target(self, obj):
        target = obj.project_target
        return TargetSerializer(target).data

    def get_is_in(self, obj):
        request = self.context.get('request')
        user_id = request.user.id
        return obj.contributors.filter(id=user_id).exists()

    def get_my_quantity(self, obj):
        request = self.context.get('request')
        user_id = request.user.id
        return obj.task_set.filter(contributor=user_id).count()


class ProjectInlineUserSerializer(ProjectSerializer):
    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'tags',
            'tags_detail',
            'project_type',
            'project_type_name',
            'founder',
            'contributors',
            'contributors_char',
            'inspector',
            'quiz',
            'quiz_name',
            'accuracy_requirement',
            'repetition_rate',
            'description',
            'verify_status',
            'status',
            'private',
            'deadline',
            'quantity',
            'project_status',
            'is_completed',
            'progress',
            'project_target',
            'target',
            'project_file',
            'is_in',
            'my_quantity',
            'uri',
        ]
        read_only_fields = ['founder', 'verify_status', 'status', 'contributors']


class ProjectReleaseSerializer(ProjectSerializer):
    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'founder',
            'description',
            'verify_status',
        ]
        read_only_fields = ['name', 'founder', 'description', 'verify_status']


class ProjectInlineVerifySerializer(ProjectSerializer):
    verify_status = serializers.ChoiceField(default='verification succeed', choices=VERIFY_STATUS_TYPE)

    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'project_type',
            'project_type_name',
            'founder',
            'description',
            'deadline',
            'verify_status',
            'project_file',
            'uri',
        ]
        read_only_fields = ['name', 'project_type', 'founder', 'description', 'deadline', 'verify_status', 'project_file',]


class ProjectTargetSerializer(ProjectSerializer):
    class Meta:
        model = Project
        fields = [
            'project_target',
            'target',
        ]


class ProjectResultURLSerializer(ProjectSerializer):
    class Meta:
        model = Project
        fields = [
            'project_status',
            'quantity',
            'result_file',
        ]
