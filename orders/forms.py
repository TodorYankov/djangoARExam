# orders/forms.py
from django import forms
from django.forms import inlineformset_factory  # 👈 добавен импорт
from .models import Order, OrderItem

# ──────────────────────────────────────
# Форми за поръчка
# ──────────────────────────────────────
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'customer_email', 'customer_phone', 'address', 'is_completed']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Име'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'имейл@пример.com'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0888 123 456'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Адрес'}),
            'is_completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'customer_name': 'Име',
            'customer_email': 'Имейл',
            'customer_phone': 'Телефон',
            'address': 'Адрес',
            'is_completed': 'Изпълнена',
        }

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'customer_email', 'customer_phone', 'address']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Име'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'имейл@пример.com'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0888 123 456'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Адрес'}),
        }
        labels = {
            'customer_name': 'Име',
            'customer_email': 'Имейл',
            'customer_phone': 'Телефон',
            'address': 'Адрес',
        }

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['is_completed']
        widgets = {
            'is_completed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_completed': 'Поръчката е изпълнена',
        }

# ──────────────────────────────────────
# Форма за артикул
# ──────────────────────────────────────
class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
        labels = {
            'product': 'Продукт',
            'quantity': 'Количество',
        }

# ──────────────────────────────────────
# Formset за артикули (inline)
# ──────────────────────────────────────
OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,      # използва готовата форма
    extra=1,
    can_delete=True,
)
