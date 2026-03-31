# orders/urls.py
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Списък с поръчки
    path('', views.OrderListView.as_view(), name='order_list'),

    # Количка + AJAX API
    path('cart/', views.cart_view, name='cart'),
    path('cart/api/', views.cart_api, name='cart_api'),
    path('cart/update/<int:product_id>/', views.update_cart_item, name='update_cart_item'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    # AJAX статистика
    path('stats/api/', views.statistics_api, name='statistics_api'),

    # Създаване на поръчка
    path('create/', views.order_create, name='order_create'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),

    # Детайли / редакция / изтриване
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('<int:pk>/update/', views.OrderUpdateView.as_view(), name='order_update'),
    path('<int:pk>/delete/', views.OrderDeleteView.as_view(), name='order_delete'),
    path('<int:pk>/status/', views.OrderStatusUpdateView.as_view(), name='order_status_update'),

    # Артикули към поръчка
    path('<int:order_id>/items/add/', views.OrderItemCreateView.as_view(), name='order_item_add'),
]

