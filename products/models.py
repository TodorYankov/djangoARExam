from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Име на категорията')
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Създадено на')

    class Meta:
        verbose_name = 'Категория'  # 👈 единично
        verbose_name_plural = 'Категории'  # 👈 множествено число
        ordering = ['name']

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Име на марката')
    country = models.CharField(max_length=50, verbose_name='Държава')
    website = models.URLField(blank=True, verbose_name='Уебсайт')

    class Meta:
        verbose_name = 'Марка'  # 👈 единично
        verbose_name_plural = 'Марки'  # 👈 множествено число
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    LAPTOP = 'laptop'
    ACCESSORY = 'accessory'
    COMPONENT = 'component'
    OTHER = 'other'

    PRODUCT_TYPES = [
        (LAPTOP, 'Ноутбук'),
        (ACCESSORY, 'Аксесоар'),
        (COMPONENT, 'Компонент'),
        (OTHER, 'Други'),
    ]

    name = models.CharField(max_length=200, verbose_name='Име на продукта')
    description = models.TextField(verbose_name='Описание')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='Цена'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Категория'
    )
    brand = models.ForeignKey(
        Brand,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name='Марка'
    )
    product_type = models.CharField(
        max_length=20,
        choices=PRODUCT_TYPES,
        default=LAPTOP,
        verbose_name='Тип на продукта'
    )
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name='Налично количество')
    is_available = models.BooleanField(default=True, verbose_name='Наличен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Създадено на')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновено на')

    # Много към много за подобни продукти
    related_products = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=True,
        verbose_name='Свързани продукти'
    )

    class Meta:
        verbose_name = 'Продукт'  # 👈 единично
        verbose_name_plural = 'Продукти'  # 👈 множествено число
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Автоматично актуализиране на is_available въз основа на stock_quantity
        self.is_available = self.stock_quantity > 0
        super().save(*args, **kwargs)

