# orders/urls.py
from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order_list'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/api/', views.cart_api, name='cart_api'),  # <-- ДОБАВЕТЕ ТОВА
    path('cart/update/<int:product_id>/', views.update_cart_item, name='update_cart_item'),  # <-- ДОБАВЕТЕ ТОВА
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),  # <-- ДОБАВЕТЕ ТОВА
    path('create/', views.order_create, name='order_create'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('<int:pk>/update/', views.OrderUpdateView.as_view(), name='order_update'),
    path('<int:pk>/delete/', views.OrderDeleteView.as_view(), name='order_delete'),
    path('<int:pk>/status/', views.OrderStatusUpdateView.as_view(), name='order_status_update'),
    path('<int:order_id>/items/add/', views.OrderItemCreateView.as_view(), name='order_item_add'),
]
