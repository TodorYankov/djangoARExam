# orders/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Order, OrderItem


class OrderForm(forms.ModelForm):
    """Форма за административно редактиране на поръчка"""

    class Meta:
        model = Order
        fields = ['user', 'guest_name', 'guest_email', 'guest_phone', 'status']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'guest_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Име'}),
            'guest_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'имейл@пример.com'}),
            'guest_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0888 123 456'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'user': 'Потребител',
            'guest_name': 'Име (гост)',
            'guest_email': 'Имейл (гост)',
            'guest_phone': 'Телефон (гост)',
            'status': 'Статус',
        }


class OrderCreateForm(forms.ModelForm):
    """Форма за създаване на поръчка (публична)"""

    class Meta:
        model = Order
        fields = ['guest_name', 'guest_email', 'guest_phone']
        widgets = {
            'guest_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Вашето име'}),
            'guest_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'имейл@пример.com'}),
            'guest_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0888 123 456'}),
        }
        labels = {
            'guest_name': 'Име',
            'guest_email': 'Имейл',
            'guest_phone': 'Телефон',
        }

    def clean_guest_phone(self):
        phone = self.cleaned_data.get('guest_phone')
        if phone:
            # Премахване на всички нецифрови символи
            import re
            cleaned = re.sub(r'[\s\(\)\-]', '', phone)
            if not re.match(r'^[0-9]{10,15}$', cleaned):
                raise forms.ValidationError('Моля, въведете валиден телефонен номер.')
            return cleaned
        return phone


class OrderStatusForm(forms.ModelForm):
    """Форма за обновяване на статуса на поръчка"""

    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class OrderItemForm(forms.ModelForm):
    """Форма за артикул в поръчка"""

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

    def clean_quantity(self):
        quantity = self.cleaned_data.get('quantity')
        if quantity and quantity <= 0:
            raise forms.ValidationError('Количеството трябва да бъде поне 1.')
        return quantity


OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,
    can_delete=True,
    fields=['product', 'quantity']
)
