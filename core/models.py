# core/models.py
from django.db import models
from django.contrib.auth.models import User


# Модел за потребителски профил  (One-to-One с User)
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    newsletter_subscription = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username
