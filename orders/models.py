# orders/models.py
from django.db import models
from django.conf import settings
from products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Чакаща'),
        ('processing', 'Обработва се'),
        ('shipped', 'Изпратена'),
        ('delivered', 'Доставена'),
        ('cancelled', 'Отказана'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Потребител'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата на създаване')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата на обновяване')

    # Данни за гост потребител
    guest_name = models.CharField(max_length=100, blank=True, verbose_name='Име (гост)')
    guest_email = models.EmailField(blank=True, verbose_name='Имейл (гост)')
    guest_phone = models.CharField(max_length=15, blank=True, verbose_name='Телефон (гост)')

    shipping_address = models.TextField(blank=True, verbose_name='Адрес за доставка')
    notes = models.TextField(blank=True, verbose_name='Бележки към поръчката')

    # НОВО ПОЛЕ - обща сума на поръчката (заявена в базата данни)
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Обща сума'
    )

    class Meta:
        verbose_name = 'Поръчка'
        verbose_name_plural = 'Поръчки'
        ordering = ['-created_at']

    def __str__(self):
        if self.user:
            return f"Поръчка {self.id} - {self.user.username}"
        return f"Поръчка {self.id} - {self.guest_name or 'Гост'}"

    @property
    def total_amount_calculated(self):
        """Изчислява общата сума на поръчката от items (за използване при нужда)"""
        return sum(item.get_total() for item in self.items.all())

    @property
    def customer_name(self):
        """Име на клиента за шаблоните"""
        if self.user:
            full_name = self.user.get_full_name().strip()
            return full_name or self.user.username
        return self.guest_name or 'Гост'

    @property
    def customer_email(self):
        """Имейл на клиента за шаблоните"""
        if self.user and self.user.email:
            return self.user.email
        return self.guest_email or '-'

    @property
    def customer_phone(self):
        """Телефон на клиента за шаблоните"""
        if self.user and hasattr(self.user, 'phone_number') and self.user.phone_number:
            return self.user.phone_number
        return self.guest_phone or '-'

    @property
    def address(self):
        """Адрес за шаблоните"""
        return self.shipping_address or '-'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)

    def get_total(self):
        return self.quantity * self.price_at_time

    def __str__(self):
        return f"{self.product} x {self.quantity}"
