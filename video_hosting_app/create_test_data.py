import random

from django.contrib.auth.models import User
from datetime import timedelta

from django.utils import timezone

from .models import VideoFile, Video


def create_test_data():
    Video.objects.all().delete()
    VideoFile.objects.all().delete()
    User.objects.all().delete()
    print('Tables cleared')
    users = []
    videos = []
    video_files = []
    for i in range(1, 10001):
        user = User(
            username=f'user_{i}',
            email=f'user_{i}@mail.ru',
            password='123456',
        )
        print(f'{user.username} created')
        users.append(user)
    User.objects.bulk_create(users)

    for i in range(1, 100001):
        owner = random.choice(users)
        video = Video(
            owner=owner,
            is_published=random.choice([True, False]),
            name=f'Видео {i}',
            created_at=timezone.now() - timedelta(days=random.randint(1, 365)),
        )
        print(f'{video.name} created')
        videos.append(video)
    Video.objects.bulk_create(videos)
    videos = Video.objects.all()

    for video in videos:
        for quality in ['HD', 'FHD', 'UHD']:
            VideoFile(
                video=video,
                file=f'videos/video_{quality}.mp4',
                quality=quality,
            )
            print(f'id - {video.id}, {video.name} {quality} created')
            video_files.append(video)


    VideoFile.objects.bulk_create(video_files)



create_test_data()