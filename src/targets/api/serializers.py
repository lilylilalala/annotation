from rest_framework import serializers

from targets.models import Target


TARGET_TYPE = {
    '0': '类目目标',
    '1': '关键字目标',
    '2': '实体目标',
}


class TargetSerializer(serializers.ModelSerializer):
    type_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Target
        fields = [
            'id',
            'user',
            'name',
            'type',
            'type_name',
            'entity',
            'description',
        ]
        read_only_fields = ['user']

    def get_type_name(self, obj):
        return TARGET_TYPE[obj.type]
