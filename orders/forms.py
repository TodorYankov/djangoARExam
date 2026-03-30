# orders/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Order, OrderItem


class OrderForm(forms.ModelForm):
    """Форма за административно редактиране на поръчка"""

    class Meta:
        model = Order
        fields = ['user', 'guest_name', 'guest_email', 'guest_phone', 'status', 'shipping_address', 'notes']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-select'}),
            'guest_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Име'}),
            'guest_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'имейл@пример.com'}),
            'guest_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0888 123 456'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'shipping_address': forms.Textarea(
                attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Адрес за доставка'}),
            'notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control', 'placeholder': 'Бележки към поръчката'}),
        }
        labels = {
            'user': 'Потребител',
            'guest_name': 'Име (гост)',
            'guest_email': 'Имейл (гост)',
            'guest_phone': 'Телефон (гост)',
            'status': 'Статус',
            'shipping_address': 'Адрес за доставка',
            'notes': 'Бележки',
        }


class OrderCreateForm(forms.ModelForm):
    """Форма за създаване на поръчка от потребител"""

    class Meta:
        model = Order
        fields = ['shipping_address', 'guest_phone', 'notes']
        widgets = {
            'shipping_address': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'град, улица, номер, вход, етаж'
            }),
            'guest_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '0888 123 456'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 2,
                'class': 'form-control',
                'placeholder': 'Допълнителна информация (вход, етаж, междучасови, специални изисквания)'
            }),
        }
        labels = {
            'shipping_address': 'Адрес за доставка',
            'guest_phone': 'Телефон',
            'notes': 'Бележки към поръчката',
        }
        help_texts = {
            'shipping_address': 'Моля, въведете пълен адрес (град, улица, номер, етаж, вход)',
            'guest_phone': 'Телефон за връзка при доставка',
            'notes': 'Допълнителна информация (вход, етаж, междучасови, специални изисквания)',
        }

    def __init__(self, *args, **kwargs):
        """Зарежда данни от профила на потребителя, ако има"""
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk:
            return

        if self.request and self.request.user.is_authenticated:
            user = self.request.user

            # Попълваме адрес от профила
            shipping_address = user.shipping_address or user.address
            if shipping_address and not self.initial.get('shipping_address'):
                self.initial['shipping_address'] = shipping_address

            # Попълваме телефон от профила
            if user.phone_number and not self.initial.get('guest_phone'):
                self.initial['guest_phone'] = user.phone_number

    def clean_guest_phone(self):
        """Валидация на телефонен номер"""
        phone = self.cleaned_data.get('guest_phone')
        if phone:
            import re
            cleaned = re.sub(r'[\s\(\)\-]', '', phone)
            if not re.match(r'^[0-9]{10,15}$', cleaned):
                raise forms.ValidationError('Моля, въведете валиден телефонен номер (10-15 цифри).')
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
        fields = ['product', 'quantity', 'price_at_time']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'price_at_time': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels = {
            'product': 'Продукт',
            'quantity': 'Количество',
            'price_at_time': 'Цена',
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
    fields=['product', 'quantity', 'price_at_time']
)



