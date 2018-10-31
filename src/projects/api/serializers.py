from rest_framework import serializers
from rest_framework.reverse import reverse as api_reverse

from projects.models import Project
from targets.api.serializers import TargetSerializer
from tags.api.serializers import TagBriefSerializer
from quizzes.models import QuizStatus

VERIFY_CHOICE = (
    ('passed', '审核通过'),
    ('failed', '审核不通过'),
)


class ProjectSerializer(serializers.ModelSerializer):
    uri = serializers.SerializerMethodField(read_only=True)
    project_type_name = serializers.SerializerMethodField(read_only=True)
    quiz_name = serializers.SerializerMethodField(read_only=True)
    quantity = serializers.SerializerMethodField(read_only=True)
    copies = serializers.SerializerMethodField(read_only=True)
    progress = serializers.SerializerMethodField(read_only=True)
    tags_detail = serializers.SerializerMethodField(read_only=False)
    target = serializers.SerializerMethodField(read_only=True)
    is_in = serializers.SerializerMethodField(read_only=True)
    my_quantity = serializers.SerializerMethodField(read_only=True)
    my_status = serializers.SerializerMethodField(read_only=True)

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
            'status',
            'status_name',
            'private',
            'deadline',
            'quantity',
            'copies',
            'progress',
            'project_target',
            'target',
            'project_file',
            'is_in',
            'my_status',
            'my_quantity',
            'uri',
        ]
        read_only_fields = ['founder', 'status', 'contributors']

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

        project_type_obj = data.get('project_type')
        target_type = project_type_obj.type
        repetition_rate = data.get('repetition_rate')
        inspector = data.get('inspector')
        if target_type.name != 'Classification':
            if inspector or repetition_rate != 1.0:
                raise serializers.ValidationError(
                    "Only Classification projects may have a inspector or a repetition rate unequal to 1.0."
                )
        else:
            if repetition_rate == 1.0:
                if inspector:
                    raise serializers.ValidationError(
                        "No need to include a inspector since repetition rate is 1.0."
                    )
            else:
                if not inspector:
                    raise serializers.ValidationError(
                        "Classification projects must have a inspector since repetition rate unequal to 1.0."
                    )
        return data

    def get_uri(self, obj):
        request = self.context.get('request')
        return api_reverse('api-projects:detail', kwargs={'id': obj.id}, request=request)

    def get_project_type_name(self, obj):
        return obj.project_type.chinese_name

    def get_quiz_name(self, obj):
        if obj.quiz:
            return obj.quiz.name
        else:
            return None

    def get_quantity(self, obj):
        return obj.quantity

    def get_copies(self, obj):
        return obj.copies

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
        user = request.user
        if obj.quantity != 0:
            return obj.contribution_set.filter(contributor=user).exclude(label='').count()
        return 0

    def get_my_status(self, obj):
        request = self.context.get('request')
        user = request.user
        quiz = obj.quiz
        if quiz:
            if quiz.quizcontributor_set.filter(contributor=user):
                qc = quiz.quizcontributor_set.get(contributor=user)
                if qc.status == QuizStatus(pk='submitted'):
                    if qc.accuracy < obj.accuracy_requirement:
                        return 'quiz_failed'
                    else:
                        return 'go_to_task'
                else:
                    return 'go_to_quiz'
            else:
                return 'go_to_quiz'
        else:
            return 'go_to_task'


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
            'status',
            'status_name',
            'private',
            'deadline',
            'quantity',
            'copies',
            'progress',
            'project_target',
            'target',
            'project_file',
            'is_in',
            'my_status',
            'my_quantity',
            'uri',
        ]
        read_only_fields = ['founder', 'status', 'contributors']


class ProjectReleaseSerializer(ProjectSerializer):
    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'founder',
            'description',
            'status',
            'status_name',
        ]
        read_only_fields = ['name', 'founder', 'description', 'status']


class ProjectInlineVerifySerializer(ProjectSerializer):
    verify_status = serializers.ChoiceField(default='passed', choices=VERIFY_CHOICE)

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
            'verify_status_name',
            'project_file',
            'uri',
        ]
        read_only_fields = ['name', 'project_type', 'founder', 'description', 'deadline', 'project_file']


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
            'status',
            'status_name',
            'quantity',
            'result_file',
        ]


class ProjectQuizSerializer(ProjectSerializer):
    class Meta:
        model = Project
        fields = [
            'id',
            'name',
        ]
