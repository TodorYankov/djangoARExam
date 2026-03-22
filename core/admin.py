# core/admin.py
from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """Admin панел за съобщения"""
    list_display = ['name', 'email', 'subject', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at']  # Не правете всички полета readonly
    actions = ['mark_as_read']

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} съобщения са маркирани като прочетени.")
    mark_as_read.short_description = "Маркирай като прочетени"

    def has_add_permission(self, request):
        # Забранява добавяне на съобщения от admin-а
        return False
