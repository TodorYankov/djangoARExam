# reviews/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from products.models import Product

User = get_user_model()


class Review(models.Model):
    """Модел за отзиви към продукти"""

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Продукт'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Потребител'
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Оценка'
    )
    title = models.CharField(max_length=100, verbose_name='Заглавие')
    comment = models.TextField(verbose_name='Коментар')
    is_approved = models.BooleanField(default=False, verbose_name='Одобрен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Създаден на')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновен на')

    class Meta:
        ordering = ['-created_at']
        unique_together = ['product', 'user']  # Един потребител - един отзив на продукт
        verbose_name = 'Отзив'
        verbose_name_plural = 'Отзиви'

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating}★"

    def save(self, *args, **kwargs):
        """При създаване на отзив, обновява средния рейтинг на продукта"""
        super().save(*args, **kwargs)
        self.product.update_average_rating()


class ReviewVote(models.Model):
    """Модел за гласуване на отзиви (полезен/неполезен)"""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='votes',
        verbose_name='Отзив'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='review_votes',
        verbose_name='Потребител'
    )
    is_helpful = models.BooleanField(verbose_name='Полезен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Създаден на')

    class Meta:
        unique_together = ['review', 'user']
        verbose_name = 'Глас за отзив'
        verbose_name_plural = 'Гласове за отзиви'

    def __str__(self):
        return f"{self.user.username} - {'Полезен' if self.is_helpful else 'Неполезен'}"

