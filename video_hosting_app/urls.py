from django.urls import path
# from rest_framework import routers
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .apps import VideoHostingAppConfig
from .views import UserCreateAPIView, VideoViewSet

app_name = VideoHostingAppConfig.name

# router = routers.DefaultRouter()
# router.register(r'', VideoViewSet, basename='')
urlpatterns = [
    path('login/', TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name='login'),
    path('logout/', TokenRefreshView.as_view(), name='logout'),
    path('register/', UserCreateAPIView.as_view(), name='register'),
    path('', VideoViewSet.as_view({'get': 'list'}), name='list'),
    path('<int:pk>/', VideoViewSet.as_view({'get': 'retrieve'}), name='retrieve'),
]