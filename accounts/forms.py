# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
# from django.utils.translation import gettext_lazy as _   # Това е импорт за интернационализация (превод на текстове), който е необходим, ако поддържам множество езици.
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
                  'phone_number', 'address', 'date_of_birth')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
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
                  'phone_number', 'address', 'date_of_birth',
                  'profile_picture', 'newsletter_subscribed')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'address': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'ул. Примерна 123, София 1000'
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

        # Направете username полето read-only (пример за read-only поле)
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

        # Добавяне на help_text
        self.fields['phone_number'].help_text = 'Въведете телефон за връзка (напр. 0888 123 456)'
        self.fields['address'].help_text = 'Въведете пълен адрес за доставка'
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
        """Валидация на профилна снимка"""
        picture = self.cleaned_data.get('profile_picture')
        if picture:
            # Проверка за размер (макс 5MB)
            if picture.size > 5 * 1024 * 1024:
                raise ValidationError('Файлът е твърде голям. Максималният размер е 5MB.')

            # Проверка за тип на файла
            valid_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
            if picture.content_type not in valid_types:
                raise ValidationError('Моля, качете валидно изображение (JPG, PNG, GIF, WebP).')

        return picture


class ProfilePictureForm(forms.ModelForm):
    """
    Отделна форма само за профилна снимка (пример за форма с едно поле)
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

        if not picture:
            raise ValidationError('Моля, изберете файл за качване.')

        # Проверка за размер
        if picture.size > 5 * 1024 * 1024:
            raise ValidationError('Файлът е твърде голям. Максималният размер е 5MB.')

        # Проверка за тип
        valid_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
        if picture.content_type not in valid_types:
            raise ValidationError('Моля, качете валидно изображение (JPG, PNG, GIF, WebP).')

        return picture


# Допълнителна форма за търсене и филтриране на потребители (за бъдеща употреба)
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
