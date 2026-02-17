# orders/admin.py
from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    fields = ('product', 'quantity')  # само съществуващи полета
    readonly_fields = []  # без 'price_at_time' ако не е добавено


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'created_at', 'is_completed', 'total_price')
    readonly_fields = ('created_at', 'total_price')
    list_display_links = ('id', 'customer_name')
    list_filter = ('is_completed', 'created_at')
    search_fields = ('customer_name', 'customer_email', 'customer_phone', 'id')
    readonly_fields = ('created_at',)  # само created_at е auto_now_add
    inlines = [OrderItemInline]

    fieldsets = (
        ('Клиент', {
            'fields': ('customer_name', 'customer_email', 'customer_phone', 'address')
        }),
        ('Детайли', {
            'fields': ('created_at', 'is_completed')
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price_at_time', 'item_total')
    readonly_fields = ('price_at_time', 'item_total')  # само за преглед
    list_filter = ('order__is_completed',)  # филтър по статус на поръчката
    search_fields = ('order__customer_name', 'product__title')
    raw_id_fields = ('order', 'product')
