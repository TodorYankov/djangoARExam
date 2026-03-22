# orders/models.py
from django.db import models
from django.conf import settings
from products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Чакаща'),
        ('processing', 'Обработва се'),
        ('completed', 'Завършена'),
        ('cancelled', 'Отказана'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Потребител'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Поля за гост потребители (ако са нужни)
    guest_name = models.CharField(max_length=100, blank=True, verbose_name='Име')
    guest_email = models.EmailField(blank=True, verbose_name='Имейл')
    guest_phone = models.CharField(max_length=20, blank=True, verbose_name='Телефон')

    @property
    def total_amount(self):
        return sum(item.get_total() for item in self.items.all())

    @property
    def customer_name(self):
        if self.user:
            return self.user.get_full_name() or self.user.username
        return self.guest_name or 'Гост'

    @property
    def customer_email(self):
        if self.user:
            return self.user.email
        return self.guest_email

    @property
    def customer_phone(self):
        if self.user and hasattr(self.user, 'phone_number'):
            return self.user.phone_number
        return self.guest_phone


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total(self):
        return self.quantity * self.price_at_time

