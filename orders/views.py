# orders/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q

from .models import Order, OrderItem
from .forms import OrderForm, OrderCreateForm, OrderItemFormSet, OrderStatusForm, OrderItemForm
from products.models import Product


# ========== ДОБАВЯНЕ В КОЛИЧКАТА ==========
@login_required
def add_to_cart(request, product_id):
    """Добавя продукт в количката (сесия)"""
    product = get_object_or_404(Product, id=product_id, is_available=True)

    # Инициализиране на количката в сесията, ако не съществува
    if 'cart' not in request.session:
        request.session['cart'] = []

    cart = request.session['cart']

    # Проверка дали продуктът вече е в количката
    found = False
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += 1
            found = True
            break

    if not found:
        cart.append({
            'product_id': product.id,
            'name': product.name,
            'price': float(product.price),
            'quantity': 1,
            'image': product.image.url if product.image else None
        })

    request.session['cart'] = cart
    messages.success(request, f'{product.name} беше добавен в количката!')

    return redirect(request.META.get('HTTP_REFERER', 'products:product_list'))


# ========== ПУБЛИЧНА ФУНКЦИЯ ЗА СЪЗДАВАНЕ НА ПОРЪЧКА ==========
def order_create(request):
    """Създаване на нова поръчка"""
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        formset = OrderItemFormSet(request.POST, prefix='items')

        if form.is_valid() and formset.is_valid():
            # 1. Записваме поръчката
            order = form.save(commit=False)

            # Ако потребителят е логнат, свързваме поръчката с него
            if request.user.is_authenticated:
                order.user = request.user

            order.save()

            # 2. Записваме артикулите
            items = formset.save(commit=False)
            for item in items:
                item.order = order
                # Взимаме актуалната цена от продукта
                item.price_at_time = item.product.price if item.product.price else 0
                item.save()

            # 3. Изтриваме маркираните за изтриване артикули
            for item in formset.deleted_objects:
                item.delete()

            # 4. Изчистване на количката след успешна поръчка
            if 'cart' in request.session:
                del request.session['cart']

            messages.success(request, 'Благодарим за поръчката! Ще се свържем с вас.')
            return redirect('orders:order_detail', pk=order.id)
        else:
            # Показване на грешки
            messages.error(request, 'Моля, поправете грешките във формата.')
    else:
        # GET заявка – показваме празна форма
        form = OrderCreateForm()
        empty_order = Order()
        formset = OrderItemFormSet(instance=empty_order, prefix='items')

    return render(request, 'orders/order_form.html', {
        'form': form,
        'formset': formset,
    })


# ========== КЛАСОВИ ИЗГЛЕДИ ==========
class OrderListView(ListView):
    """Списък с поръчки"""
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        queryset = Order.objects.all()

        # Филтриране по състояние
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Търсене
        search_query = self.request.GET.get('search')
        if search_query:
            # Първо провери дали не търси ID
            if search_query.isdigit():
                queryset = queryset.filter(id=int(search_query))
            else:
                # Търсене по име на клиент (от профила или от поръчката)
                queryset = queryset.filter(
                    Q(user__first_name__icontains=search_query) |
                    Q(user__last_name__icontains=search_query) |
                    Q(user__username__icontains=search_query) |
                    Q(user__email__icontains=search_query)
                )

        return queryset.order_by('-created_at')


class OrderDetailView(DetailView):
    """Детайли на поръчка"""
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'


class OrderCreateView(CreateView):
    """Създаване на поръчка (административно)"""
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('orders:order_list')


class OrderUpdateView(UpdateView):
    """Редактиране на поръчка"""
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('orders:order_list')


class OrderDeleteView(DeleteView):
    """Изтриване на поръчка"""
    model = Order
    template_name = 'orders/order_confirm_delete.html'
    success_url = reverse_lazy('orders:order_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Изтриване на поръчка #{self.object.id}"
        return context


class OrderStatusUpdateView(UpdateView):
    """Обновяване на статуса на поръчка"""
    model = Order
    form_class = OrderStatusForm
    template_name = 'orders/order_status_form.html'
    success_url = reverse_lazy('orders:order_list')


class OrderItemCreateView(CreateView):
    """Добавяне на артикул към поръчка"""
    model = OrderItem
    form_class = OrderItemForm
    template_name = 'orders/orderitem_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order'] = get_object_or_404(Order, id=self.kwargs['order_id'])
        return context

    def form_valid(self, form):
        order = get_object_or_404(Order, id=self.kwargs['order_id'])
        order_item = form.save(commit=False)
        order_item.order = order
        order_item.price_at_time = order_item.product.price
        order_item.save()
        messages.success(self.request, f'Артикулът {order_item.product.name} беше добавен към поръчката.')
        return redirect('orders:order_detail', pk=order.id)
