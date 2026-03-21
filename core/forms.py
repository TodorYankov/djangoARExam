# core/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """
    Форма за контакт
    """

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Вашето име'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@mail.com'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Тема на съобщението'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Вашето съобщение...'
            }),
        }

    def clean_name(self):
        """Валидация на име"""
        name = self.cleaned_data.get('name')
        if name and len(name) < 2:
            raise ValidationError('Името трябва да съдържа поне 2 символа.')
        return name

    def clean_message(self):
        """Валидация на съобщение"""
        message = self.cleaned_data.get('message')
        if message and len(message) < 10:
            raise ValidationError('Съобщението трябва да съдържа поне 10 символа.')
        return message


class NewsletterForm(forms.Form):
    """
    Форма за абонамент за бюлетин
    """
    email = forms.EmailField(
        label='Имейл',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Вашият имейл адрес'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError('Моля, въведете имейл адрес.')
        return email
