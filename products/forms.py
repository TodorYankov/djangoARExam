# products/forms
from django import forms
from .models import Product, Category
from django.core.validators import MinValueValidator


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['related_products', 'is_available', 'created_at', 'updated_at']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Въведете описание на продукта...',
                'class': 'form-control'
            }),
            'name': forms.TextInput(attrs={
                'placeholder': 'Например: HP Compaq',
                'class': 'form-control'
            }),
            'price': forms.NumberInput(attrs={
                'min': '0',
                'step': '0.01',
                'class': 'form-control'
            }),
            'stock_quantity': forms.NumberInput(attrs={
                'min': '0',
                'class': 'form-control'
            }),
        }
        labels = {
            'name': 'Име на продукт',
            'price': 'Цена (€.)',
            'stock_quantity': 'Наличност',
        }
        help_texts = {
            'price': 'Въведете цена в евро',
            'stock_quantity': 'Брой налични продукти',
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price <= 0:
            raise forms.ValidationError("Цената трябва да е положително число!")
        return price

    def clean_stock_quantity(self):
        quantity = self.cleaned_data.get('stock_quantity')
        if quantity < 0:
            raise forms.ValidationError("Наличността не може да е отрицателна!")
        return quantity


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Например: Игрови лаптопи',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Кратко описание на категорията...',
                'class': 'form-control'
            }),
        }
