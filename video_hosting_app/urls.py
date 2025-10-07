from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import UserCreateAPIView

app_name = 'video_hosting_app'

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name='login'),
    path('logout/', TokenRefreshView.as_view(), name='logout'),
    path('register/', UserCreateAPIView.as_view(), name='register'),
]