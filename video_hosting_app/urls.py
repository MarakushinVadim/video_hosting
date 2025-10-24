from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .apps import VideoHostingAppConfig
from .views import UserCreateAPIView, VideoViewSet, LikeViewSet, IDViewSet, SubQueryViewSet, CroupByViewSet

app_name = VideoHostingAppConfig.name

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name='login'),
    path('logout/', TokenRefreshView.as_view(), name='logout'),
    path('register/', UserCreateAPIView.as_view(), name='register'),
    path('', VideoViewSet.as_view({'get': 'list'}), name='list'),
    path('<int:pk>/', VideoViewSet.as_view({'get': 'retrieve'}), name='retrieve'),
    path('<int:video_id>/like/', LikeViewSet.as_view({'post': 'create'}), name='like'),
    path('ids/', IDViewSet.as_view({'get': 'list'}), name='ids_list'),
    path('statistics-subquery/', SubQueryViewSet.as_view({'get': 'list'}), name='statistics_subquery'),
    path('statistics-group-by/', CroupByViewSet.as_view({'get': 'list'}), name='statistics-group-by'),
]
