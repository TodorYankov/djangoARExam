# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    """
    Персонализиран административен интерфейс за CustomUser модела
    """
    model = CustomUser

    # ========== КОЛОНИ В СПИСЪКА ==========
    list_display = [
        'profile_picture_thumbnail',
        'username',
        'email',
        'first_name',
        'last_name',
        'formatted_phone',
        'user_age',
        'is_staff',
        'loyalty_points',
        'newsletter_subscribed',
        'date_joined'
    ]

    # ========== ФИЛТРИ ==========
    list_filter = [
        'is_staff',
        'is_superuser',
        'is_active',
        'groups',
        'newsletter_subscribed',
        'date_joined',
        'date_of_birth'
    ]

    # ========== ТЪРСЕНЕ ==========
    search_fields = [
        'username',
        'email',
        'first_name',
        'last_name',
        'phone_number',
        'address'
    ]

    # ========== ПОЛЕТА ЗА РЕДАКТИРАНЕ ==========
    fieldsets = UserAdmin.fieldsets + (
        (_('Лична информация'), {
            'fields': ('phone_number', 'address', 'date_of_birth', 'profile_picture')
        }),
        (_('Настройки и предпочитания'), {
            'fields': ('newsletter_subscribed', 'loyalty_points'),
            'classes': ('collapse',)
        }),
    )

    # ========== ПОЛЕТА ЗА ДОБАВЯНЕ НА НОВ ПОТРЕБИТЕЛ ==========
    add_fieldsets = UserAdmin.add_fieldsets + (
        (_('Лична информация'), {
            'fields': ('phone_number', 'address', 'date_of_birth', 'profile_picture')
        }),
        (_('Настройки'), {
            'fields': ('newsletter_subscribed',),
            'classes': ('collapse',)
        }),
    )

    # ========== ПОЛЕТА САМО ЗА ЧЕТЕНЕ ==========
    readonly_fields = ['date_joined', 'last_login']

    # ========== ПОДРЕЖДАНЕ ==========
    ordering = ['-date_joined']

    # ========== ДЕЙСТВИЯ ЗА МАСОВА ОБРАБОТКА ==========
    actions = [
        'activate_users',
        'deactivate_users',
        'add_loyalty_points_100',
        'subscribe_to_newsletter',
        'unsubscribe_from_newsletter',
        'make_staff',
        'remove_staff'
    ]

    # ========== ПЕРСОНАЛИЗИРАНИ МЕТОДИ ЗА КОЛОНИ ==========
    def profile_picture_thumbnail(self, obj):
        """Показва миниатюра на профилната снимка"""
        if obj.profile_picture and obj.profile_picture.url:
            return format_html(
                '<img src="{}" width="40" height="40" style="border-radius: 50%; object-fit: cover;" />',
                obj.profile_picture.url
            )
        return format_html('<span style="color: #999;">📷 Без снимка</span>')

    profile_picture_thumbnail.short_description = _('Снимка')

    def formatted_phone(self, obj):
        """Показва форматиран телефонен номер"""
        if obj.phone_number:
            phone = obj.phone_number
            # Премахване на всички нецифрови символи
            digits = ''.join(filter(str.isdigit, phone))
            if len(digits) == 10:
                return f"{digits[:4]} {digits[4:7]} {digits[7:]}"
            return phone
        return '—'

    formatted_phone.short_description = _('Телефон')
    formatted_phone.admin_order_field = 'phone_number'

    def user_age(self, obj):
        """Показва възрастта на потребителя"""
        age = obj.age
        if age:
            return f"{age} г."
        return '—'

    user_age.short_description = _('Възраст')
    user_age.admin_order_field = 'date_of_birth'

    # ========== МАСОВИ ДЕЙСТВИЯ ==========
    def activate_users(self, request, queryset):
        """Активира избраните потребители"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'✅ {updated} потребители бяха активирани успешно.',
            messages.SUCCESS
        )

    activate_users.short_description = _('Активирай избраните потребители')

    def deactivate_users(self, request, queryset):
        """Деактивира избраните потребители"""
        # Предотвратява деактивиране на суперпотребители
        superusers = queryset.filter(is_superuser=True)
        if superusers.exists():
            self.message_user(
                request,
                f'⚠️ Не можете да деактивирате {superusers.count()} суперпотребител(и)!',
                messages.ERROR
            )
            queryset = queryset.filter(is_superuser=False)

        updated = queryset.update(is_active=False)
        if updated > 0:
            self.message_user(
                request,
                f'🔒 {updated} потребители бяха деактивирани.',
                messages.WARNING
            )

    deactivate_users.short_description = _('Деактивирай избраните потребители')

    def add_loyalty_points_100(self, request, queryset):
        """Добавя 100 точки за лоялност"""
        for user in queryset:
            user.add_loyalty_points(100)

        self.message_user(
            request,
            f'⭐ 100 точки за лоялност бяха добавени на {queryset.count()} потребители.',
            messages.SUCCESS
        )

    add_loyalty_points_100.short_description = _('Добави 100 точки за лоялност')

    def subscribe_to_newsletter(self, request, queryset):
        """Абонира за бюлетин"""
        updated = queryset.update(newsletter_subscribed=True)
        self.message_user(
            request,
            f'📧 {updated} потребители бяха абонирани за бюлетин.',
            messages.SUCCESS
        )

    subscribe_to_newsletter.short_description = _('Абонирай за бюлетин')

    def unsubscribe_from_newsletter(self, request, queryset):
        """Отписва от бюлетин"""
        updated = queryset.update(newsletter_subscribed=False)
        self.message_user(
            request,
            f'📧 {updated} потребители бяха отписани от бюлетин.',
            messages.INFO
        )

    unsubscribe_from_newsletter.short_description = _('Отпиши от бюлетин')

    def make_staff(self, request, queryset):
        """Дава персонални права"""
        updated = queryset.update(is_staff=True)
        self.message_user(
            request,
            f'👥 {updated} потребители получиха персонални права.',
            messages.SUCCESS
        )

    make_staff.short_description = _('Дай персонални права')

    def remove_staff(self, request, queryset):
        """Премахва персонални права"""
        # Предотвратява премахване на права от суперпотребители
        superusers = queryset.filter(is_superuser=True)
        if superusers.exists():
            self.message_user(
                request,
                f'⚠️ Не можете да премахнете правата на {superusers.count()} суперпотребител(и)!',
                messages.ERROR
            )
            queryset = queryset.filter(is_superuser=False)

        updated = queryset.update(is_staff=False)
        if updated > 0:
            self.message_user(
                request,
                f'👥 {updated} потребители загубиха персонални права.',
                messages.WARNING
            )

    remove_staff.short_description = _('Премахни персонални права')

    # ========== СИГУРНОСТ ==========
    def delete_model(self, request, obj):
        """Предотвратява изтриване на суперпотребители"""
        if obj.is_superuser:
            self.message_user(
                request,
                '❌ Не можете да изтриете суперпотребител!',
                messages.ERROR
            )
        else:
            super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """Предотвратява масово изтриване на суперпотребители"""
        superusers = queryset.filter(is_superuser=True)
        if superusers.exists():
            self.message_user(
                request,
                f'❌ Не можете да изтриете {superusers.count()} суперпотребител(и)! Изтрийте ги отделно.',
                messages.ERROR
            )
            queryset = queryset.filter(is_superuser=False)

        if queryset.exists():
            super().delete_queryset(request, queryset)


# Регистриране на модела в административния интерфейс
admin.site.register(CustomUser, CustomUserAdmin)

