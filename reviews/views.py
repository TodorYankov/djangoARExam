# reviews/views.py
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from products.models import Product
from .models import Review
from .forms import ReviewForm


class ReviewCreateView(LoginRequiredMixin, CreateView):
    """Изглед за създаване на отзив"""
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/review_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.product = get_object_or_404(Product, pk=kwargs['product_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = self.product
        return context

    def form_valid(self, form):
        form.instance.product = self.product
        form.instance.user = self.request.user

        # Проверка дали потребителят вече е оставил отзив
        if Review.objects.filter(product=self.product, user=self.request.user).exists():
            messages.error(self.request, 'Вече сте оставили отзив за този продукт.')
            return redirect('products:detail', pk=self.product.pk)

        messages.success(self.request, 'Отзивът ви беше изпратен успешно! Очаквайте одобрение.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('products:detail', kwargs={'pk': self.product.pk})


class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Изглед за обновяване на отзив"""
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/review_form.html'

    def test_func(self):
        review = self.get_object()
        return self.request.user == review.user or self.request.user.is_staff

    def get_success_url(self):
        return reverse_lazy('products:detail', kwargs={'pk': self.object.product.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Отзивът ви беше обновен успешно!')
        return super().form_valid(form)


class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Изглед за изтриване на отзив"""
    model = Review
    template_name = 'reviews/review_confirm_delete.html'

    def test_func(self):
        review = self.get_object()
        return self.request.user == review.user or self.request.user.is_staff

    def get_success_url(self):
        return reverse_lazy('products:detail', kwargs={'pk': self.object.product.pk})

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Отзивът беше изтрит успешно!')
        return super().delete(request, *args, **kwargs)


class ReviewListView(ListView):
    """Изглед за списък с отзиви"""
    model = Review
    template_name = 'reviews/review_list.html'
    paginate_by = 10
    context_object_name = 'reviews'

    def get_queryset(self):
        queryset = Review.objects.filter(is_approved=True)

        # Филтриране по продукт
        product_id = self.request.GET.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)

        # Филтриране по рейтинг
        rating = self.request.GET.get('rating')
        if rating:
            queryset = queryset.filter(rating=rating)

        # Сортиране
        sort = self.request.GET.get('sort', '-created_at')
        if sort in ['rating', '-rating', 'created_at', '-created_at']:
            queryset = queryset.order_by(sort)

        return queryset.select_related('user', 'product')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_reviews'] = self.get_queryset().count()
        context['average_rating'] = self.get_queryset().aggregate(models.Avg('rating'))['rating__avg']
        return context

