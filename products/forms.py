# products/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import Product, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock_quantity',
                  'category', 'product_type', 'image', 'related_products']  # 👈 Добавихме related_products
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Въведете име на продукта'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Подробно описание на продукта...'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'product_type': forms.Select(attrs={'class': 'form-select'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'related_products': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
            # 👈 Добавихме widget за related_products
        }
        labels = {
            'name': 'Име на продукт',
            'description': 'Описание',
            'price': 'Цена (лв.)',
            'stock_quantity': 'Наличност (брой)',
            'category': 'Категория',
            'product_type': 'Тип продукт',
            'image': 'Снимка',
            'related_products': 'Свързани продукти',
        }
        help_texts = {
            'price': 'Въведете положително число (пример: 49.99)',
            'stock_quantity': 'Брой налични бройки в склада',
            'image': 'Качете снимка на продукта (JPEG, PNG)',
            'related_products': 'Изберете продукти, които са свързани с този (задръжте Ctrl за множествен избор)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Проверка за категории - променяме визуализацията
        if not Category.objects.exists():
            # Ако няма категории, показваме предупреждение
            self.fields['category'].empty_label = "--- НЯМА КАТЕГОРИИ ---"
            self.fields['category'].queryset = Category.objects.none()
            # Добавяме CSS клас за червена рамка
            self.fields['category'].widget.attrs.update({
                'style': 'border: 2px solid #dc3545; background-color: #fff3f3;'
            })

    def clean(self):
        cleaned_data = super().clean()

        # Проверка за категории само при създаване на нов продукт
        if not self.instance.pk:  # Това е нов продукт (не редактиране)
            if not Category.objects.exists():
                raise ValidationError(
                    '❌ Не можете да създадете продукт, защото няма създадени категории. '
                    'Моля, първо създайте категория.'
                )

        return cleaned_data

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price <= 0:
            raise ValidationError('Цената трябва да бъде положително число!')
        return price

    def clean_stock_quantity(self):
        stock = self.cleaned_data.get('stock_quantity')
        if stock is not None and stock < 0:
            raise ValidationError('Наличността не може да бъде отрицателно число!')
        return stock


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Например: Лаптопи, Аксесоари...'}),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Описание на категорията...'}),
        }
        labels = {
            'name': 'Име на категория',
            'description': 'Описание',
        }
        help_texts = {
            'name': 'Въведете уникално име на категорията',
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        # Проверка за уникалност
        if self.instance.pk:  # При редакция
            if Category.objects.exclude(pk=self.instance.pk).filter(name=name).exists():
                raise ValidationError('Категория с това име вече съществува!')
        else:  # При създаване
            if Category.objects.filter(name=name).exists():
                raise ValidationError('Категория с това име вече съществува!')
        return name

