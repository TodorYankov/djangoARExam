# orders/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem


class IsCompletedFilter(admin.SimpleListFilter):
    title = 'Завършена поръчка'
    parameter_name = 'is_completed'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Да'),
            ('no', 'Не'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(status='delivered')
        if self.value() == 'no':
            return queryset.exclude(status='delivered')
        return queryset


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ['product', 'quantity', 'price_at_time', 'item_total']
    readonly_fields = ['item_total']

    def item_total(self, obj):
        return f'{obj.get_total():.2f} €'

    item_total.short_description = 'Общо'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'guest_name', 'guest_email', 'guest_phone',
                    'created_at', 'status', 'colored_status', 'is_completed_display', 'total_price_display']
    list_filter = ['status', 'created_at', IsCompletedFilter]
    search_fields = ['guest_name', 'guest_email', 'guest_phone', 'user__username', 'user__email']
    inlines = [OrderItemInline]
    readonly_fields = ['created_at', 'updated_at', 'total_price_display']

    fieldsets = (
        ('Информация за клиента', {
            'fields': ('user', 'guest_name', 'guest_email', 'guest_phone', 'shipping_address')
        }),
        ('Статус и дати', {
            'fields': ('status', 'created_at', 'updated_at', 'notes', 'total_price_display')
        }),
    )

    def colored_status(self, obj):
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'shipped': 'purple',
            'delivered': 'green',
            'cancelled': 'red',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )

    colored_status.short_description = 'Статус'
    colored_status.admin_order_field = 'status'

    def is_completed_display(self, obj):
        return obj.status == 'delivered'

    is_completed_display.short_description = 'Завършена'
    is_completed_display.boolean = True

    def total_price_display(self, obj):
        total = sum(item.get_total() for item in obj.items.all())
        return f'{total:.2f} €'

    total_price_display.short_description = 'Обща сума'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'price_at_time', 'item_total']
    list_filter = ['order__status']
    search_fields = ['order__guest_name', 'product__name', 'order__user__username']

    def item_total(self, obj):
        return f'{obj.get_total():.2f} €'

    item_total.short_description = 'Общо'
