from django.contrib import admin

from .models import Like, Video, VideoFile


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'video')
    list_filter = ('video',)
    search_fields = ('user', 'video')

@admin.register(VideoFile)
class VideoFileAdmin(admin.ModelAdmin):
    list_display = ('video', 'quality')
    list_filter = ('video',)
    search_fields = ('video',)

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ('owner', 'name', 'total_likes', 'created_at', 'is_published')
    list_filter = ('owner', 'is_published',)
    search_fields = ('owner', 'name')