# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from datetime import date
from .models import CustomUser
import re


class CustomUserCreationForm(UserCreationForm):
    """
    Форма за регистрация на нов потребител
    """
    email = forms.EmailField(
        required=True,
        label='Имейл',
        widget=forms.EmailInput(attrs={
            'placeholder': 'example@mail.com',
            'class': 'form-control'
        })
    )

    phone_number = forms.CharField(
        required=False,
        label='Телефон',
        widget=forms.TextInput(attrs={
            'placeholder': '0888 123 456',
            'class': 'form-control'
        })
    )

    # НОВО: Добавен адрес за доставка
    shipping_address = forms.CharField(
        required=False,
        label='Адрес за доставка',
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'град, улица, номер, вход, етаж',
            'class': 'form-control'
        })
    )

    # Добавяне на поле за потвърждение на имейл
    confirm_email = forms.EmailField(
        required=True,
        label='Потвърдете имейл',
        widget=forms.EmailInput(attrs={
            'placeholder': 'example@mail.com',
            'class': 'form-control'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name',
                  'phone_number', 'shipping_address', 'address', 'date_of_birth')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(
                attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Друг адрес (ако е различен)'}),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }

    def clean_email(self):
        """Валидация за уникален имейл"""
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.filter(email=email).exists():
            raise ValidationError('Потребител с този имейл вече съществува.')
        return email

    def clean_confirm_email(self):
        """Валидация за съвпадение на имейлите"""
        email = self.cleaned_data.get('email')
        confirm_email = self.cleaned_data.get('confirm_email')

        if email and confirm_email and email != confirm_email:
            raise ValidationError('Имейлите не съвпадат.')
        return confirm_email

    def clean_phone_number(self):
        """Валидация на телефонен номер"""
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Премахване на интервали и специални символи
            cleaned_phone = re.sub(r'[\s\(\)\-]', '', phone)
            if not re.match(r'^\+?[0-9]{10,15}$', cleaned_phone):
                raise ValidationError('Моля, въведете валиден телефонен номер (10-15 цифри).')
            return cleaned_phone
        return phone

    def clean_date_of_birth(self):
        """Валидация на дата на раждане"""
        dob = self.cleaned_data.get('date_of_birth')

        if not dob:
            return dob

        # Проверка за бъдеща дата
        if dob > date.today():
            raise ValidationError('Датата на раждане не може да бъде в бъдещето.')

        # Проверка за минимална възраст (16 години)
        age = date.today().year - dob.year
        if (date.today().month, date.today().day) < (dob.month, dob.day):
            age -= 1

        if age < 16:
            raise ValidationError(f'Трябва да сте поне на 16 години. Вашата възраст е {age} години.')

        if age > 120:
            raise ValidationError('Моля, въведете валидна дата на раждане.')

        return dob

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data.get('phone_number')  # Мапиране към phone
        user.shipping_address = self.cleaned_data.get('shipping_address')
        if commit:
            user.save()
            # Автоматично добавяне към група Customers
            from django.contrib.auth.models import Group
            customers_group, _ = Group.objects.get_or_create(name='Customers')
            user.groups.add(customers_group)
        return user


class CustomUserChangeForm(UserChangeForm):
    """
    Форма за редактиране на потребителски профил
    """
    password = None  # Скриване на полето за парола

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name',
                  'phone_number', 'shipping_address', 'date_of_birth',
                  'profile_picture', 'newsletter_subscribed')
        # ЗАБЕЛЕЖКА: Премахнах 'address' от полетата, за да не се използва
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'shipping_address': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'град, улица, номер, вход, етаж'
            }),
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*'
            }),
            'newsletter_subscribed': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Направете username полето read-only
        self.fields['username'].widget.attrs['readonly'] = True
        self.fields['username'].help_text = 'Потребителското име не може да се променя'

        # Направете имейла задължителен
        self.fields['email'].required = True

        # Добавяне на Bootstrap класове към всички полета
        for field_name, field in self.fields.items():
            if field_name not in ['profile_picture', 'newsletter_subscribed']:
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'form-control'

        # Персонализиране на лейбълите
        self.fields['first_name'].label = 'Име'
        self.fields['last_name'].label = 'Фамилия'
        self.fields['newsletter_subscribed'].label = 'Абонамент за бюлетин'
        self.fields['profile_picture'].label = 'Профилна снимка'
        self.fields['shipping_address'].label = 'Адрес за доставка'

        # Добавяне на help_text
        self.fields['phone_number'].help_text = 'Въведете телефон за връзка (напр. 0888 123 456)'
        self.fields['shipping_address'].help_text = 'Въведете пълен адрес за доставка (град, улица, номер, вход, етаж)'
        self.fields['profile_picture'].help_text = 'Качете снимка (макс. 5MB, формати: JPG, PNG, GIF)'

    def clean_email(self):
        """Валидация за уникален имейл (без текущия потребител)"""
        email = self.cleaned_data.get('email')
        if email and CustomUser.objects.exclude(pk=self.instance.pk).filter(email=email).exists():
            raise ValidationError('Потребител с този имейл вече съществува.')
        return email

    def clean_phone_number(self):
        """Валидация на телефонен номер"""
        phone = self.cleaned_data.get('phone_number')
        if phone:
            cleaned_phone = re.sub(r'[\s\(\)\-]', '', phone)
            if not re.match(r'^\+?[0-9]{10,15}$', cleaned_phone):
                raise ValidationError('Моля, въведете валиден телефонен номер (10-15 цифри).')
            return cleaned_phone
        return phone

    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')

        # Проверка дали няма качен файл
        if not picture:
            return picture

        # Проверка дали е празен низ (случва се при празно поле за снимка)
        if picture == '':
            return None

        # След това безопасно проверяваме content_type
        valid_types = ['image/jpeg', 'image/png', 'image/gif']

        # За качени файлове, проверяваме content_type
        if hasattr(picture, 'content_type'):
            if picture.content_type not in valid_types:
                raise forms.ValidationError('Моля, качете снимка във формат JPEG, PNG или GIF.')
        else:
            # Ако няма content_type, определяме от разширението на файла
            import imghdr
            import os

            # Взимаме разширението на файла
            ext = os.path.splitext(picture.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.gif']:
                raise forms.ValidationError('Моля, качете снимка във формат JPEG, PNG или GIF.')

        return picture

    def save(self, commit=True):
        user = super().save(commit=False)
        # Мапиране на phone_number към phone (за съвместимост)
        user.phone = self.cleaned_data.get('phone_number')
        # shipping_address вече се запазва автоматично от формата
        if commit:
            user.save()
        return user


class ProfilePictureForm(forms.ModelForm):
    """
    Отделна форма само за профилна снимка
    """

    class Meta:
        model = CustomUser
        fields = ('profile_picture',)
        widgets = {
            'profile_picture': forms.FileInput(attrs={
                'class': 'form-control-file',
                'accept': 'image/*',
                'id': 'profile-picture-input'
            })
        }
        labels = {
            'profile_picture': 'Качете нова профилна снимка'
        }
        help_texts = {
            'profile_picture': 'Поддържани формати: JPG, PNG, GIF, WebP. Максимален размер: 5MB'
        }

    def clean_profile_picture(self):
        """Валидация на профилна снимка"""
        picture = self.cleaned_data.get('profile_picture')

        # Ако няма файл - не правим нищо
        if not picture:
            return picture

        # Ако е празен низ (случва се при празно поле)
        if picture == '':
            return None

        # Проверка за размер
        if picture.size > 5 * 1024 * 1024:
            raise ValidationError('Файлът е твърде голям. Максималният размер е 5MB.')

        # Проверка за тип - безопасно проверяваме дали има content_type
        valid_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']

        if hasattr(picture, 'content_type'):
            if picture.content_type not in valid_types:
                raise ValidationError('Моля, качете валидно изображение (JPG, PNG, GIF, WebP).')
        else:
            # Ако няма content_type, проверяваме разширението
            import os
            ext = os.path.splitext(picture.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                raise ValidationError('Моля, качете валидно изображение (JPG, PNG, GIF, WebP).')

        return picture


# Форма за търсене и филтриране на потребители
class UserSearchForm(forms.Form):
    """
    Форма за търсене на потребители
    """
    username = forms.CharField(
        required=False,
        label='Потребителско име',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Търси по username'})
    )
    email = forms.EmailField(
        required=False,
        label='Имейл',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Търси по имейл'})
    )
    is_staff = forms.BooleanField(
        required=False,
        label='Само персонал',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    newsletter_subscribed = forms.BooleanField(
        required=False,
        label='Абонирани за бюлетин',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
