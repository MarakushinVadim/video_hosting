from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Like, Video, VideoFile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')


class VideoFileSerializer(serializers.ModelSerializer):
    quality_display = serializers.SerializerMethodField()

    class Meta:
        model = VideoFile
        fields = ('file', 'quality_display')

    def get_quality_display(self, obj):
        return obj.get_quality_display()


class VideoSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    video_files = VideoFileSerializer(many=True, read_only=True, source='videofile_set')

    class Meta:
        model = Video
        fields = (
            'id',
            'is_published',
            'owner',
            'name',
            'total_likes',
            'created_at',
            'video_files',
        )


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'
