# orders/models.py
from django.core.validators import RegexValidator
from django.db import models
from products.models import Product
from django.core.exceptions import ValidationError


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Чакащо'),
        ('processing', 'Обработва се'),
        ('completed', 'Завършено'),
        ('cancelled', 'Отказано'),
    ]

    # По-гъвкав валидатор - позволява цифри, интервали, тирета, + и ()
    phone_regex = RegexValidator(
        regex=r'^[\d\s\+\-\(\)]{9,20}$',
        message="Телефонният номер трябва да съдържа между 9 и 20 символа: цифри, +, -, (), интервали."
    )

    customer_phone = models.CharField(
        max_length=20,
        validators=[phone_regex],
        verbose_name='Телефон'
    )

    customer_name = models.CharField(max_length=100, verbose_name='Име')
    customer_email = models.EmailField(verbose_name='Имейл')

    # Само ЕДНО дефиниране на customer_phone (с валидатора)
    customer_phone = models.CharField(
        max_length=20,
        validators=[phone_regex],
        verbose_name='Телефон'
    )

    address = models.TextField(verbose_name='Адрес')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )

    class Meta:
        verbose_name = 'Поръчка'
        verbose_name_plural = 'Поръчки'
        ordering = ['-created_at']

    @property
    def total_price(self):
        return sum(item.item_total for item in self.items.all())

    @property
    def is_completed(self):
        # Дефинирайте вашата логика тук, например:
        return self.status == 'completed'

    def __str__(self):
        return f"Поръчка #{self.id} - {self.customer_name}"

    def clean(self):
        # Тази валидация ще се изпълнява само за съществуващи поръчки
        if self.pk and not self.items.exists():
            raise ValidationError('Поръчката трябва да съдържа поне един продукт')

        # За нови поръчки пропускаме проверката

    def save(self, *args, **kwargs):
        # За нови обекти не изпълняваме full_clean преди запис
        if not self.pk:
            super().save(*args, **kwargs)
        else:
            self.full_clean()
            super().save(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена при поръчка')

    def save(self, *args, **kwargs):
        if not self.price_at_time:  # Ако няма цена, вземи текущата от продукта
            self.price_at_time = self.product.price
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Артикул в поръчка'
        verbose_name_plural = 'Артикули в поръчки'

    @property
    def item_total(self):
        """Обща цена за този конкретен артикул (количество × цена)"""
        return self.quantity * self.price_at_time

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def clean(self):
        if self.quantity > self.product.stock_quantity:
            raise ValidationError(f'Наличността на {self.product.name} е само {self.product.stock_quantity} бройки')
