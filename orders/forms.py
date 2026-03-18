# orders/forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Order, OrderItem

# ──────────────────────────────────────
# Форми за поръчка
# ──────────────────────────────────────
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'customer_email', 'customer_phone', 'address', 'status']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Име'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'имейл@пример.com'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '0888 123 456'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Адрес'}),
            'status': forms.Select(attrs={'class': 'form-select'}),  # 👈 добавете това
        }
        labels = {
            'customer_name': 'Име',
            'customer_email': 'Имейл',
            'customer_phone': 'Телефон',
            'address': 'Адрес',
            'status': 'Статус',  # 👈 променено от is_completed
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
    # Създаваме поле, което не е свързано директно с модела
    is_completed = forms.BooleanField(
        required=False,
        label='Поръчката е изпълнена',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Order
        fields = ['status']  # само status, без is_completed

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Задаваме началната стойност от property-то
            self.fields['is_completed'].initial = self.instance.is_completed

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Ако is_completed е отметнато, сменяме статуса на 'completed'
        if self.cleaned_data.get('is_completed'):
            instance.status = 'completed'
        if commit:
            instance.save()
        return instance

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
    form=OrderItemForm,
    extra=1,
    can_delete=True,
)