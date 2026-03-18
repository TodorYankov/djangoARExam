#orders/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem


# Custom филтър за is_completed
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
            return queryset.filter(status='completed')
        if self.value() == 'no':
            return queryset.exclude(status='completed')
        return queryset


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ['product', 'quantity', 'price_at_time', 'item_total']
    readonly_fields = ['item_total']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'customer_email', 'customer_phone',
                    'created_at', 'status', 'colored_status', 'is_completed_display', 'total_price']
    list_filter = ['status', 'created_at', IsCompletedFilter]  # 👈 Добавете custom филтъра
    search_fields = ['customer_name', 'customer_email', 'customer_phone', 'address']
    inlines = [OrderItemInline]
    readonly_fields = ['total_price', 'created_at']

    fieldsets = (
        ('Информация за клиента', {
            'fields': ('customer_name', 'customer_email', 'customer_phone', 'address')
        }),
        ('Статус и дата', {
            'fields': ('status', 'created_at', 'total_price')
        }),
    )

    def colored_status(self, obj):
        colors = {
            'pending': 'orange',
            'processing': 'blue',
            'completed': 'green',
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
        return 'Да' if obj.is_completed else 'Не'

    is_completed_display.short_description = 'Завършена'
    is_completed_display.boolean = True

    def total_price(self, obj):
        return f'{obj.total_price:.2f} лв.'

    total_price.short_description = 'Обща сума'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'price_at_time', 'item_total']
    list_filter = ['order__status']  # Филтър по статус на поръчката
    search_fields = ['order__customer_name', 'product__name']

    def item_total(self, obj):
        return f'{obj.item_total:.2f} лв.'

    item_total.short_description = 'Общо'
