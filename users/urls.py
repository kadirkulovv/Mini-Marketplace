from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, extend_schema_view
from .views import RegisterView, UserProfileView

DecoratedTokenObtainPairView = extend_schema_view(
    post=extend_schema(tags=['Autentifikatsiya'], summary='Tizimga kirish (JWT token olish)')
)(TokenObtainPairView)

DecoratedTokenRefreshView = extend_schema_view(
    post=extend_schema(tags=['Autentifikatsiya'], summary='Access tokenni yangilash')
)(TokenRefreshView)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', DecoratedTokenObtainPairView.as_view(), name='login'),
    path('refresh/', DecoratedTokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='profile'),
]

