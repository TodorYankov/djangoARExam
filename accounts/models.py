# accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from datetime import date
import os


def validate_image_file(value):
    """
    Валидация за файлове - само изображения
    """
    # Проверка на разширението
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']

    if ext not in valid_extensions:
        raise ValidationError(
            f'Моля, качете валидно изображение. Разрешени формати: {", ".join(valid_extensions)}'
        )

    # Проверка за размер на файла (макс 5MB)
    max_size = 5 * 1024 * 1024  # 5MB в байтове
    if value.size > max_size:
        raise ValidationError(
            f'Файлът е твърде голям. Максималният размер е 5MB. '
            f'Вашият файл е {value.size / (1024 * 1024):.1f}MB.'
        )


class CustomUser(AbstractUser):
    """
    Разширен потребителски модел с допълнителни полета за TechShop

    Този модел разширява стандартния Django User с допълнителни полета:
    - Телефонен номер
    - Адрес за доставка
    - Дата на раждане
    - Профилна снимка
    - Абонамент за бюлетин
    - Точки за лоялност
<<<<<<< HEAD
    - Любими продукти (Many-to-many)
=======
>>>>>>> 029e97a88d363c55a2af3c732061de53b5bb95f1
    """

    # ========== КОНТАКТНИ ПОЛЕТА ==========
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        verbose_name=_('Телефон'),
        help_text=_('Мобилен телефон за връзка (във формат 0888 123 456)')
    )

    address = models.TextField(
        blank=True,
        verbose_name=_('Адрес'),
        help_text=_('Адрес за доставка (улица, номер, град, пощенски код)')
    )

    # ========== ЛИЧНА ИНФОРМАЦИЯ ==========
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Дата на раждане'),
        help_text=_('Моля, въведете дата на раждане (формат: ГГГГ-ММ-ДД)')
    )

    profile_picture = models.ImageField(
        upload_to='profiles/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name=_('Профилна снимка'),
        help_text=_('Качете профилна снимка (макс. 5MB, формати: JPG, PNG, GIF, WebP)'),
        validators=[validate_image_file]
    )

    # ========== НАСТРОЙКИ И ПРЕДПОЧИТАНИЯ ==========
    newsletter_subscribed = models.BooleanField(
        default=True,
        verbose_name=_('Абонамент за бюлетин'),
        help_text=_('Желая да получавам имейли за нови продукти и промоции')
    )

    loyalty_points = models.IntegerField(
        default=0,
        verbose_name=_('Точки за лоялност'),
        help_text=_('Точки за лоялност, които могат да се използват за отстъпки')
    )

<<<<<<< HEAD
    # ========== MANY-TO-MANY ВРЪЗКА ==========
    # Любими продукти - Many-to-many връзка с Product модела
    favourites = models.ManyToManyField(
        'products.Product',
        blank=True,
        related_name='favourited_by',
        verbose_name=_('Любими продукти'),
        help_text=_('Продукти, които потребителят е добавил в любими')
    )

=======
>>>>>>> 029e97a88d363c55a2af3c732061de53b5bb95f1
    # ========== МЕТАДАННИ ==========
    class Meta:
        permissions = [
            ("can_view_reports", "Може да преглежда отчети"),
            ("can_manage_inventory", "Може да управлява наличности"),
            ("can_manage_orders", "Може да управлява всички поръчки"),
        ]
        verbose_name = _('Потребител')
        verbose_name_plural = _('Потребители')
        ordering = ['-date_joined']

    # ========== МЕТОДИ ==========
    def __str__(self):
        """Текстово представяне на потребителя"""
        return f"{self.username} ({self.email})"

    def clean(self):
        """Валидация на модела преди запис в базата данни"""
        super().clean()

        # Валидация на дата на раждане
        if self.date_of_birth:
            # Проверка 1: Датата не може да е в бъдещето
            if self.date_of_birth > date.today():
                raise ValidationError({
                    'date_of_birth': _('Датата на раждане не може да бъде в бъдещето.')
                })

            # Проверка 2: Изчисляване на точната възраст
            today = date.today()
            age = today.year - self.date_of_birth.year

            # Корекция, ако рожденият ден все още не е настъпил тази година
            if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
                age -= 1

            # Проверка 3: Минимална възраст (16 години)
            if age < 16:
                raise ValidationError({
                    'date_of_birth': _(
                        f'Трябва да сте поне на 16 години, за да се регистрирате. '
                        f'Вашата възраст е {age} години.'
                    )
                })

            # Проверка 4: Максимална възраст (120 години)
            if age > 120:
                raise ValidationError({
                    'date_of_birth': _(
                        'Моля, въведете валидна дата на раждане. '
                        'Възрастта не може да надвишава 120 години.'
                    )
                })

    def save(self, *args, **kwargs):
        """Презаписване на save метода за гарантирана валидация"""
        self.full_clean()
        super().save(*args, **kwargs)

    def get_full_name(self):
        """Връща пълното име или username, ако няма име и фамилия"""
        full_name = super().get_full_name()
        return full_name if full_name else self.username

    @property
    def age(self):
        """Изчислява възрастта на потребителя"""
        if not self.date_of_birth:
            return None

        today = date.today()
        age = today.year - self.date_of_birth.year

        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1

        return age

    @property
    def is_staff_member(self):
        """Проверка дали потребителят е част от Staff групата"""
        return self.groups.filter(name='Staff').exists() or self.is_superuser

    @property
    def profile_picture_url(self):
        """Връща URL на профилната снимка или default аватар"""
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return '/static/images/default-avatar.png'

    @property
    def formatted_phone(self):
        """Връща форматиран телефонен номер за показване"""
        if not self.phone_number:
            return 'Не е въведен'

        if len(self.phone_number) == 10 and self.phone_number.isdigit():
            return f"{self.phone_number[:4]} {self.phone_number[4:7]} {self.phone_number[7:]}"
        return self.phone_number

    @property
    def has_complete_profile(self):
        """Проверка дали профилът е пълен"""
        return bool(
            self.first_name and
            self.last_name and
            self.phone_number and
            self.address and
            self.date_of_birth
        )

    def add_loyalty_points(self, points):
        """Добавя точки за лоялност към потребителя"""
        if points > 0:
            self.loyalty_points += points
            self.save(update_fields=['loyalty_points'])
            return True
        return False

    def use_loyalty_points(self, points):
        """Използва точки за лоялност"""
        if 0 < points <= self.loyalty_points:
            self.loyalty_points -= points
            self.save(update_fields=['loyalty_points'])
            return True
        return False

<<<<<<< HEAD
    def add_to_favourites(self, product):
        """Добавя продукт към любимите"""
        if product not in self.favourites.all():
            self.favourites.add(product)
            return True
        return False

    def remove_from_favourites(self, product):
        """Премахва продукт от любимите"""
        if product in self.favourites.all():
            self.favourites.remove(product)
            return True
        return False

    def is_favourite(self, product):
        """Проверява дали продуктът е в любимите"""
        return self.favourites.filter(id=product.id).exists()

=======
>>>>>>> 029e97a88d363c55a2af3c732061de53b5bb95f1

