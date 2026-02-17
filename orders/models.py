# order/models.py
from django.db import models
from products.models import Product


class Order(models.Model):
    customer_name = models.CharField(max_length=100, verbose_name='Име')
    customer_email = models.EmailField(verbose_name='Имейл')
    customer_phone = models.CharField(max_length=20, verbose_name='Телефон')
    address = models.TextField(verbose_name='Адрес')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    is_completed = models.BooleanField(default=False, verbose_name='Изпълнена')

    @property
    def total_price(self):
        """Обща стойност на поръчката (сума от item_total на всички артикули)"""
        return sum(item.item_total for item in self.items.all())

    def __str__(self):
        return f"Поръчка #{self.id} - {self.customer_name}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена при поръчка')

    @property
    def item_total(self):
        """Обща цена за този конкретен артикул (количество × цена)"""
        return self.quantity * self.price_at_time

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
