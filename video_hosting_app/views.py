from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Like, Video, VideoFile
from .pagination import MyPagination
from .permissions import IsOwner
from .serializers import LikeSerializer, UserSerializer, VideoSerializer, VideoFileSerializer


class UserCreateAPIView(APIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    http_method_names = ('post',)


    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = serializer.save(is_active=True)
            user.set_password(user.password)
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VideoViewSet(ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    pagination_class = MyPagination


    def perform_create(self, serializer):
        video = serializer.save()
        video.owner = self.request.user
        video.save()

    def list(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            queryset = Video.objects.filter(is_published=True)
            paginated_queryset = self.paginate_queryset(queryset)
            serializer = VideoSerializer(paginated_queryset, many=True)
            return self.get_paginated_response(serializer.data)
        if self.request.user.is_staff:
            queryset = Video.objects.all()
            serializer = VideoSerializer(queryset, many=True)
            return Response(serializer.data)
        queryset = Video.objects.filter(Q(owner=self.request.user) | Q(is_published=True))
        serializer = VideoSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = (IsAuthenticated,)
        elif (
            self.action == 'update'
            or self.action == 'destroy'
            or self.action == 'partial_update'
        ):
            self.permission_classes = (IsOwner,)
        elif self.action == 'list':
            self.permission_classes = (AllowAny,)

        return super().get_permissions()


class VideoFileViewSet(viewsets.ModelViewSet):
    queryset = VideoFile.objects.all()
    serializer_class = VideoFileSerializer

    def perform_create(self, serializer):
        video_file = serializer.save()
        video_file.video = serializer.id
        video_file.save()

    def list(self, request, *args, **kwargs):
        queryset = VideoFile.objects.filter(video_id=self.kwargs['video_id'])
        serializer = VideoFileSerializer(queryset, many=True)
        return Response(serializer.data)




class LikeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        video_id = request.data.get('video_id')
        user = request.user

        if not video_id:
            return Response({'Ошибка' : 'Видео не найдено'}, status=status.HTTP_400_BAD_REQUEST)

        like_exists = Like.objects.filter(video_id=video_id, user=user).exists()
        if like_exists:
            Like.objects.get(video_id=video_id, user=user).delete()
            return Response({'message': 'Лайк удален'}, status=status.HTTP_204_NO_CONTENT)
        else:
            like = Like.objects.create(video_id=video_id, user=user)
            serializer = LikeSerializer(like)
            return Response(serializer.data, status=status.HTTP_201_CREATED)



