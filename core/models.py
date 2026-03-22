# core/models.py
from django.db import models

class ContactMessage(models.Model):
    """Модел за съобщения от контактната форма"""
    name = models.CharField(max_length=100, verbose_name='Име')
    email = models.EmailField(verbose_name='Имейл')
    subject = models.CharField(max_length=200, verbose_name='Тема', blank=True)
    message = models.TextField(verbose_name='Съобщение')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    is_read = models.BooleanField(default=False, verbose_name='Прочетено')

    class Meta:
        verbose_name = 'Съобщение за контакт'
        verbose_name_plural = 'Съобщения за контакт'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%d.%m.%Y')}"

