# products/urls.py
from products.api.views import ProductListAPIView, ProductDetailAPIView, CategoryListAPIView
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Продукти
    path('', views.ProductListView.as_view(), name='product_list'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('create/', views.ProductCreateView.as_view(), name='product_create'),
    path('<int:pk>/update/', views.ProductUpdateView.as_view(), name='product_update'),
    path('<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),

    # Категории
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/create/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/update/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),

    # API endpoints
    path('api/products/', ProductListAPIView.as_view(), name='api_product_list'),
    path('api/products/<int:pk>/', ProductDetailAPIView.as_view(), name='api_product_detail'),
    path('api/categories/', CategoryListAPIView.as_view(), name='api_category_list'),
]





