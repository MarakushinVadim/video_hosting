from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q, F, OuterRef, Sum, Subquery, Count
from django.db.models.functions import Coalesce
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Like, Video, VideoFile
from .pagination import MyPagination
from .permissions import IsOwner, IsStaff
from .serializers import (
    LikeSerializer,
    UserSerializer,
    VideoSerializer,
    VideoFileSerializer,
    IDSerializer,
)


class UserCreateAPIView(APIView):
    """
    Эндпоинт для создания пользователя на основе стандартной модели User
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    http_method_names = ("post",)

    def post(self, request, *args, **kwargs):
        """
        Метод для создания пользователя, прогоняет данные через сериализатор и если данные валидны,
        создает пользователя (устанавливает поле is_active=True) возвращает статус 201,
        если данные не валидны возвращает статус 400
        """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user = serializer.save(is_active=True)
            user.set_password(user.password)
            user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VideoViewSet(ModelViewSet):
    """
    Эндпоинт для работы с объектами класса Video
    """
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    pagination_class = MyPagination

    def perform_create(self, serializer):
        """
        При создании видео, назначает текущего пользователя владельцем видео
        """
        video = serializer.save()
        video.owner = self.request.user
        video.save()

    def retrieve(self, request, *args, **kwargs):
        """
        Метод для получения данных о конкретном видео
        """
        video = Video.objects.get(pk=kwargs["pk"])
        serializer = VideoSerializer(video)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """
        Метод для получения списка видео, возвращает данные в зависимости от прав пользователя
        """
        if not self.request.user.is_authenticated:
            queryset = Video.objects.filter(is_published=True).select_related("owner")
            paginated_queryset = self.paginate_queryset(queryset)
            serializer = VideoSerializer(paginated_queryset, many=True)
            return self.get_paginated_response(serializer.data)
        if self.request.user.is_staff:
            queryset = Video.objects.all().select_related("owner")
            serializer = VideoSerializer(queryset, many=True)
            return Response(serializer.data)
        queryset = Video.objects.filter(
            Q(owner=self.request.user) | Q(is_published=True)
        ).select_related("owner")
        serializer = VideoSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_permissions(self):
        """
        Метод для установки прав доступа для пользователей
        """
        if self.action == "create":
            self.permission_classes = (IsAuthenticated,)
        elif (
            self.action == "update"
            or self.action == "destroy"
            or self.action == "partial_update"
        ):
            self.permission_classes = (IsOwner,)
        elif self.action == "list":
            self.permission_classes = (AllowAny,)

        return super().get_permissions()


class VideoFileViewSet(viewsets.ModelViewSet):
    """
    Эндпоинт для создания видео-файлов к видео
    """
    queryset = VideoFile.objects.all()
    serializer_class = VideoFileSerializer

    def perform_create(self, serializer):
        """
        Метод для проверки валидности данных и последующего сохранения видео-файла
        """
        video_file = serializer.save()
        video_file.video = serializer.id
        video_file.save()

    def list(self, request, *args, **kwargs):
        """
        Метод для получения списка видео-файлов
        """
        queryset = VideoFile.objects.filter(video_id=self.kwargs["video_id"])
        serializer = VideoFileSerializer(queryset, many=True)
        return Response(serializer.data)


class LikeViewSet(viewsets.ModelViewSet):
    """
    Эндпоинт для создания/удаления лайков
    """
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        """
        Метод который, если на данном Видео от данного пользователя уже есть лайк - удаляет его,
         если нет - создает
        """
        try:
            with transaction.atomic():
                video_id = kwargs["video_id"]
                user = request.user

                video = Video.objects.select_for_update().get(pk=video_id)
                video_published = video.is_published

                if not video_published:
                    return Response(
                        {"Ошибка": "Опубликованного видео по запросу не найдено"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                like_exists = Like.objects.filter(video_id=video_id, user=user).exists()
                if like_exists:
                    Like.objects.filter(video_id=video_id, user=user).delete()
                    Video.objects.filter(pk=video_id).update(
                        total_likes=F("total_likes") - 1
                    )
                    return Response(
                        {"message": "Лайк удален"}, status=status.HTTP_204_NO_CONTENT
                    )
                else:
                    like = Like.objects.create(video_id=video_id, user=user)
                    Video.objects.filter(pk=video_id).update(
                        total_likes=F("total_likes") + 1
                    )

                    serializer = LikeSerializer(like)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ObjectDoesNotExist:
            return Response(
                {"Ошибка": "Видео не найдено"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"Ошибка": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class IDViewSet(viewsets.ModelViewSet):
    """
    Эндпоинт для получения списка id видео
    возвращает список c идентификаторами всех опубликованных видео, все видео за один раз, без пагинации
    доступен только служебным пользователям
    """
    permission_classes = [IsStaff]
    pagination_class = None

    def list(self, request, *args, **kwargs):
        """
        Метод, который возвращает список ID
        """
        queryset = Video.objects.filter(is_published=True)
        serializer = IDSerializer(queryset, many=True)
        return Response(serializer.data)


class SubQueryViewSet(viewsets.ModelViewSet):
    """
    Эндпоинт который, возвращают список пользователей с количеством их лайков через подзапрос
    доступен только служебным пользователям
    """
    permission_classes = [IsStaff]

    def list(self, request, *args, **kwargs):
        likes_subquery = Subquery(
            Video.objects.filter(owner_id=OuterRef("id"), is_published=True)
            .values("owner_id")
            .annotate(likes_sum=Sum("total_likes"))
            .values("likes_sum")[:1]
        )

        users = User.objects.annotate(
            likes_sum=Coalesce(Subquery(likes_subquery), 0)
        ).order_by("-likes_sum")

        result = users.values("username", "likes_sum").order_by("-likes_sum")
        return Response(result)


class CroupByViewSet(viewsets.ModelViewSet):
    """
    Эндпоинт который, возвращают список пользователей с количеством их лайков через группировку
    доступен только служебным пользователям
    """
    permission_classes = [IsStaff]

    def list(self, request, *args, **kwargs):
        users = (
            Video.objects.select_related("user")
            .values("owner__username")
            .annotate(likes_sum=Sum("total_likes"), username=F("owner__username"))
            .values("username", "likes_sum")
            .order_by("-likes_sum")
        )
        return Response(users)
