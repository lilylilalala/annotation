from rest_framework import serializers
from rest_framework.reverse import reverse as api_reverse

from tags.models import Tag


class TagSerializer(serializers.ModelSerializer):
    child = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
            'parent',
            'child',
            'level',
            'description',
            'founder',
            'updated',
        ]
        read_only_fields = ['updated', 'founder']

    def validate(self, data):
        level = data.get('level')
        parent = data.get('parent')
        if level == 1:
            if parent:
                raise serializers.ValidationError("Level 1 tag has no parent!")
            return data
        elif level == 2:
            if not parent:
                raise serializers.ValidationError("Level 2 tag must add a parent!")
            return data
        return data

    def get_child(self, obj):
        tag_id = obj.id
        child = Tag.objects.filter(parent=tag_id)
        return TagBriefSerializer(child, many=True).data


class TagBriefSerializer(TagSerializer):
    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
            'level',
        ]


class TagDetailSerializer(TagSerializer):

    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
            'parent',
            'child',
            'level',
            'description',
            'founder',
            'updated',
        ]
        read_only_fields = ['updated', 'founder', 'parent', 'level', 'description']
