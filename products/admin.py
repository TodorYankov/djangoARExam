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
        if not Category.objects.exists():
            self.fields['category'].queryset = Category.objects.none()
            self.fields['category'].empty_label = "--- НЯМА КАТЕГОРИИ ---"

    def clean_category(self):
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
    list_display_links = ('name',)
    list_filter = ('category', 'is_available', 'created_at', 'product_type')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock_quantity', 'is_available')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    filter_horizontal = ('related_products',)
    list_per_page = 25

    fieldsets = (
        ('Основна информация', {
            'fields': ('name', 'description', 'category', 'product_type')
        }),
        ('Цена и наличност', {
            'fields': ('price', 'stock_quantity', 'is_available')
        }),
        ('Снимка', {
            'fields': ('image',),
            'classes': ('collapse',)
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

    # ========== ДЕЙСТВИЯ ЗА МАСОВА ОБРАБОТКА ==========
    # Започнете без actions, след това добавяйте едно по едно
    actions = []

    # Ако искате да добавите действия, разкоментирайте и тествайте:
    """
    def make_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} продукта бяха маркирани като налични.')
    make_available.short_description = 'Маркирай като налични'

    def make_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} продукта бяха маркирани като неналични.')
    make_unavailable.short_description = 'Маркирай като неналични'

    actions = ['make_available', 'make_unavailable']
    """






