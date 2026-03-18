# products/admin.py
from django.contrib import admin
from django.contrib import messages
from django import forms
from django.utils.safestring import mark_safe
from .models import Category, Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Проверка за категории при инициализация на формата
        if not Category.objects.exists():
            self.fields['category'].queryset = Category.objects.none()
            self.fields['category'].empty_label = "--- НЯМА КАТЕГОРИИ ---"

    def clean_category(self):
        """Валидация на полето category"""
        if not Category.objects.exists():
            raise forms.ValidationError(
                mark_safe(
                    '<div style="color: #721c24; background: #f8d7da; padding: 10px;">'
                    '⚠️ Не можете да създадете продукт, защото няма категории. '
                    '<a href="/admin/products/category/add/" style="color: #721c24; font-weight: bold;">'
                    'Създайте категория</a> първо.'
                    '</div>'
                )
            )
        return self.cleaned_data['category']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_count', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('name',)

    def product_count(self, obj):
        return obj.products.count()

    product_count.short_description = 'Брой продукти'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = ('name', 'category', 'price', 'stock_quantity', 'is_available', 'created_at')
    list_filter = ('category', 'is_available', 'created_at', 'product_type')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock_quantity', 'is_available')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    filter_horizontal = ('related_products',)

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






