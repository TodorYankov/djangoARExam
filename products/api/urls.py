# products/api/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    # Product endpoints
    path('products/', views.ProductListAPIView.as_view(), name='api-product-list'),
    path('products/<int:pk>/', views.ProductDetailAPIView.as_view(), name='api-product-detail'),

    # Category endpoints
    path('categories/', views.CategoryListAPIView.as_view(), name='api-category-list'),

    # Celery task endpoints
    path('test-task/', views.test_celery_task, name='test-task'),
    path('task-status/<str:task_id>/', views.check_task_status, name='task-status'),

    # JWT Authentication
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]