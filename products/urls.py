from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryListCreateView, CategoryDetailView, ProductViewSet

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category_list_create'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),
    path('', include(router.urls)),
]

