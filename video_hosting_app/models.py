from django.db import models
from rest_framework.authtoken.admin import User


class Video(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    is_published = models.BooleanField(default=False)
    name = models.CharField(max_length=255)
    total_likes = models.PositiveIntegerField(default=0)
    crawled_at = models.DateTimeField(auto_now_add=True)

class VideoFile(models.Model):
    QUALITY_CHOICES = [
        ('HD', 'HD (720p)'),
        ('FHD', 'FHD (1080p)'),
        ('UHD', 'UHD (4k)'),
    ]
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    file = models.FileField(upload_to='videos/')
    quality = models.CharField(max_length=3, choices=QUALITY_CHOICES)

    class Meta:
        unique_together = ('video', 'quality')

class Like(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)