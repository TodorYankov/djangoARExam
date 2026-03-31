# products/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Име на категорията')
    slug = models.SlugField(unique=True, blank=True, verbose_name='URL адрес')
    description = models.TextField(blank=True, verbose_name='Описание')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Създадено на')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

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
        verbose_name="Цена (€)"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Категория'
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

    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        verbose_name='Снимка'
    )

    # Нови полета за рейтинг (за reviews app)
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        verbose_name='Среден рейтинг'
    )
    total_reviews = models.PositiveIntegerField(
        default=0,
        verbose_name='Брой отзиви'
    )

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукти'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Автоматично актуализиране на is_available въз основа на stock_quantity
        self.is_available = self.stock_quantity > 0
        super().save(*args, **kwargs)

    def update_average_rating(self):
        """Обновява средния рейтинг на продукта от одобрените отзиви"""
        # Използваме get_model за избягване на циркулярен импорт
        from django.apps import apps

        Review = apps.get_model('reviews', 'Review')

        # Взимаме само одобрените отзиви
        reviews = self.reviews.filter(is_approved=True)
        total = reviews.count()

        if total > 0:
            from django.db.models import Avg
            avg = reviews.aggregate(Avg('rating'))['rating__avg']
            self.average_rating = round(avg, 2)
        else:
            self.average_rating = 0.00

        self.total_reviews = total
        self.save(update_fields=['average_rating', 'total_reviews'])




