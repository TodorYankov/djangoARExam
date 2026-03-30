# products/api/views.py
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.conf import settings
from products.models import Product, Category
from products.api.serializers import ProductSerializer, CategorySerializer
from products.tasks import test_celery
from celery.result import AsyncResult


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


@api_view(['GET'])
def test_celery_task(request):
    """Тестова задача за Celery"""
    # Ако сме в development режим с eager tasks, изпълняваме задачата директно
    if settings.CELERY_TASK_ALWAYS_EAGER:
        # Изпълняваме задачата синхронно
        result = test_celery.apply()
        return Response({
            'task_id': 'eager_task',
            'status': 'completed',
            'message': 'Task executed synchronously (eager mode)',
            'result': result.result
        })
    else:
        # В production - използваме асинхронна задача
        task = test_celery.delay()
        return Response({
            'task_id': task.id,
            'status': 'started',
            'message': 'Test task has been queued'
        })


@api_view(['GET'])
def check_task_status(request, task_id):
    """Проверка на статус на задача"""
    if task_id == 'eager_task':
        return Response({
            'task_id': task_id,
            'status': 'SUCCESS',
            'ready': True,
            'result': {'message': 'Task executed in eager mode'}
        })

    task = AsyncResult(task_id)

    response = {
        'task_id': task_id,
        'status': task.state,
        'ready': task.ready(),
    }

    if task.ready():
        if task.successful():
            response['result'] = task.result
        else:
            response['error'] = str(task.result) if task.result else 'Task failed'

    return Response(response)
