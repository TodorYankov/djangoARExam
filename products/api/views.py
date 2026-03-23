# products/api/views.py
from rest_framework import generics, permissions
from products.models import Product, Category
from products.api.serializers import ProductSerializer, CategorySerializer

class ProductListAPIView(generics.ListAPIView):
    """API endpoint за списък с всички продукти"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

class ProductDetailAPIView(generics.RetrieveAPIView):
    """API endpoint за детайли на продукт"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

class CategoryListAPIView(generics.ListAPIView):
    """API endpoint за списък с всички категории"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
