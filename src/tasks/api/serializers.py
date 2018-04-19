from rest_framework import serializers

from tasks.models import TextClassification, ImageClassification


class TextClassificationSerializer(serializers.ModelSerializer):
    text_file_path = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TextClassification
        fields = [
            'id',
            'project',
            'text_file_path',
            'label',
        ]
        read_only_fields = ['id', 'project']

    def get_text_file_path(self, obj):
        return obj.text_file.url


class ImageClassificationSerializer(serializers.ModelSerializer):
    image_file_path = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ImageClassification
        fields = [
            'id',
            'project',
            'image_file_path',
            'label',
        ]
        read_only_fields = ['id', 'project']

    def get_image_file_path(self, obj):
        return obj.image_file.url
