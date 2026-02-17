# products/admin.py
from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_count', 'created_at')  # Променено
    search_fields = ('name', 'description')
    ordering = ('name',)

    def product_count(self, obj):
        """Показва брой продукти в категорията"""
        return obj.products.count()

    product_count.short_description = 'Брой продукти'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock_quantity', 'is_available', 'created_at')  # Променено
    list_filter = ('category','is_available', 'created_at', 'product_type')  # Добавено product_type
    search_fields = ('name', 'description')  # Променено (премахнато sku)
    list_editable = ('price', 'stock_quantity', 'is_available')  # Променено
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)

    # По-добра организация на полетата
    fieldsets = (
        ('Основна информация', {
            'fields': ('name', 'description', 'category', 'product_type')
        }),
        ('Цена и наличност', {
            'fields': ('price', 'stock_quantity', 'is_available')
        }),
        ('Свързани продукти', {
            'fields': ('related_products',),
            'classes': ('collapse',)
        }),
        ('Дати', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # За по-лесен избор на свързани продукти
    filter_horizontal = ('related_products',)



