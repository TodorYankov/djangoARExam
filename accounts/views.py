# accounts/views.py
from django.urls import reverse_lazy
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.views.generic import CreateView, UpdateView, DetailView, TemplateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm, ProfilePictureForm


class RegisterView(SuccessMessageMixin, CreateView):
    """
    Регистрация на нов потребител
    """
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:profile')
    success_message = 'Регистрацията е успешна! Добре дошли в TechShop!'

    def form_valid(self, form):
        """След валидна форма, автоматично логваме потребителя"""
        response = super().form_valid(form)

        # Автоматичен вход след регистрация
        user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1']
        )
        if user:
            login(self.request, user)
            messages.success(self.request, self.success_message)

        return response

    def get_success_url(self):
        """Пренасочване след успешна регистрация"""
        return reverse_lazy('accounts:profile')


class ProfileView(LoginRequiredMixin, DetailView):
    """
    Преглед на потребителски профил
    """
    model = CustomUser
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        """Добавя допълнителен контекст за профила"""
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Добавяне на статистика
        context['total_orders'] = user.order_set.count() if hasattr(user, 'order_set') else 0
        context['total_loyalty_points'] = user.loyalty_points
        context['profile_completion'] = self.get_profile_completion(user)

        return context

    def get_profile_completion(self, user):
        """Изчислява колко процента от профила е попълнен"""
        fields = ['first_name', 'last_name', 'phone_number', 'address', 'date_of_birth', 'profile_picture']
        filled_fields = sum(1 for field in fields if getattr(user, field, None))
        return int((filled_fields / len(fields)) * 100)


class ProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Редактиране на потребителски профил
    """
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'accounts/profile_edit.html'
    success_message = 'Профилът е обновен успешно!'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('accounts:profile')

    def form_invalid(self, form):
        """Обработка на невалидна форма"""
        messages.error(self.request, 'Моля, поправете грешките във формата.')
        return super().form_invalid(form)


class ProfileDeleteView(LoginRequiredMixin, DeleteView):
    """Изтриване на профила на потребителя"""
    model = CustomUser  # ← Променете User на CustomUser
    success_url = reverse_lazy('core:index')
    template_name = 'accounts/profile_confirm_delete.html'

    def get_object(self, queryset=None):
        return self.request.user

class ProfilePictureUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    """
    Отделна форма за качване на профилна снимка (пример за форма с едно поле)
    """
    model = CustomUser
    form_class = ProfilePictureForm
    template_name = 'accounts/profile_picture.html'
    success_message = 'Профилната снимка е обновена успешно!'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('accounts:profile')

    def form_valid(self, form):
        """След успешно качване, добавя допълнително съобщение"""
        response = super().form_valid(form)
        messages.success(self.request, self.success_message)
        return response


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Потребителски dashboard - показва поръчки, точки, активност
    """
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Поръчки на потребителя (когато свържем Order с CustomUser)
        if hasattr(user, 'order_set'):
            context['orders'] = user.order_set.all().order_by('-created_at')
            context['total_orders'] = user.order_set.count()
            # Проверка за total_amount поле
            if context['orders'] and hasattr(context['orders'][0], 'total_amount'):
                context['total_spent'] = sum(order.total_amount for order in context['orders'])
            else:
                context['total_spent'] = 0
        else:
            context['orders'] = []
            context['total_orders'] = 0
            context['total_spent'] = 0

        # Точки за лоялност
        context['loyalty_points'] = user.loyalty_points

        # Последна активност
        context['last_login'] = user.last_login

        # Статистика
        context['profile_completion'] = self.get_profile_completion(user)

        return context

    def get_profile_completion(self, user):
        """Изчислява процента на попълненост на профила"""
        fields = ['first_name', 'last_name', 'phone_number', 'address', 'date_of_birth']
        filled = sum(1 for field in fields if getattr(user, field, None))
        return int((filled / len(fields)) * 100)


class UserDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    """
    Изтриване на потребителски профил (с потвърждение)
    """
    model = CustomUser
    template_name = 'accounts/profile_delete.html'
    success_url = reverse_lazy('core:index')
    success_message = 'Вашият профил беше изтрит успешно.'

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        """Изтриване на потребителя и изход от системата"""
        user = self.get_object()
        logout(request)
        response = super().delete(request, *args, **kwargs)
        messages.success(request, self.success_message)
        return response


class UserListView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """
    Списък с всички потребители (само за персонал)
    """
    template_name = 'accounts/user_list.html'

    def test_func(self):
        """Само персонал и суперпотребители имат достъп"""
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = CustomUser.objects.all().order_by('-date_joined')
        context['total_users'] = CustomUser.objects.count()
        context['staff_count'] = CustomUser.objects.filter(is_staff=True).count()
        context['active_users'] = CustomUser.objects.filter(is_active=True).count()
        return context


class CustomLoginView(LoginView):
    """
    Персонализиран изглед за вход
    """
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('accounts:profile')

    def form_valid(self, form):
        """След успешен вход"""
        username = form.cleaned_data.get('username')
        try:
            user = CustomUser.objects.get(username=username)
            full_name = user.get_full_name()
            if full_name and full_name != username:
                messages.success(self.request, f'Добре дошли отново, {full_name}!')
            else:
                messages.success(self.request, f'Добре дошли отново, {username}!')
        except CustomUser.DoesNotExist:
            messages.success(self.request, 'Успешен вход!')

        return super().form_valid(form)


