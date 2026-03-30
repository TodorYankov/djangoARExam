# orders/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
import json
from django.http import JsonResponse
from .models import Order, OrderItem
from .forms import OrderForm, OrderCreateForm, OrderItemFormSet, OrderStatusForm, OrderItemForm
from products.models import Product


# ========== ФУНКЦИИ ЗА КОЛИЧКАТА ==========
@login_required
def cart_view(request):
    """Преглед на количката"""
    cart = request.session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    cart_count = sum(item['quantity'] for item in cart)

    context = {
        'cart': cart,
        'total': total,
        'cart_count': cart_count
    }
    return render(request, 'orders/cart.html', context)


@login_required
def update_cart_item(request, product_id):
    """Обновява количество на продукт в количката"""
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', [])

        for item in cart:
            if item['product_id'] == product_id:
                if quantity > 0:
                    item['quantity'] = quantity
                else:
                    cart.remove(item)
                break

        request.session['cart'] = cart

        # Проверка дали заявката е AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'cart_count': sum(item['quantity'] for item in cart),
                'total': sum(item['price'] * item['quantity'] for item in cart)
            })

        messages.success(request, 'Количеството беше обновено успешно.')
        return redirect('orders:cart')

    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=400)


@login_required
def remove_from_cart(request, product_id):
    """Премахва продукт от количката"""
    if request.method == 'POST':
        cart = request.session.get('cart', [])
        cart = [item for item in cart if item['product_id'] != product_id]
        request.session['cart'] = cart

        # Проверка дали заявката е AJAX (идва от JavaScript)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            # За AJAX заявки връщаме JSON
            return JsonResponse({
                'success': True,
                'cart_count': len(cart),
                'total': sum(item['price'] * item['quantity'] for item in cart)
            })

        # За нормални заявки (без JavaScript) правим redirect
        messages.success(request, 'Продуктът беше премахнат от количката.')
        return redirect('orders:cart')

    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=400)


# ========== ДОБАВЯНЕ В КОЛИЧКАТА ==========
@login_required
def add_to_cart(request, product_id):
    """Добавя продукт в количката (сесия) - с поддръжка на AJAX"""
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

    # Проверка дали заявката е AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': sum(item['quantity'] for item in cart),
            'total': sum(item['price'] * item['quantity'] for item in cart),
            'message': f'{product.name} беше добавен в количката!'
        })

    messages.success(request, f'{product.name} беше добавен в количката!')
    return redirect(request.META.get('HTTP_REFERER', 'products:product_list'))

# ========== AJAX ФУНКЦИИ ЗА КОЛИЧКАТА ==========
def cart_api(request):
    """API endpoint за количката (AJAX) - публичен достъп"""
    # Ако потребителят не е логнат, връщаме празна количка
    if not request.user.is_authenticated:
        return JsonResponse({
            'cart': [],
            'total': 0,
            'cart_count': 0
        })

    if request.method == 'GET':
        cart = request.session.get('cart', [])
        total = sum(item['price'] * item['quantity'] for item in cart)
        return JsonResponse({
            'cart': cart,
            'total': total,
            'cart_count': sum(item['quantity'] for item in cart)
        })

    elif request.method == 'POST':
        data = json.loads(request.body)
        action = data.get('action')
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)

        cart = request.session.get('cart', [])

        if action == 'add':
            # Добавяне на продукт
            found = False
            for item in cart:
                if item['product_id'] == product_id:
                    item['quantity'] += quantity
                    found = True
                    break
            if not found:
                product = get_object_or_404(Product, id=product_id)
                cart.append({
                    'product_id': product.id,
                    'name': product.name,
                    'price': float(product.price),
                    'quantity': quantity,
                    'image': product.image.url if product.image else None
                })

        elif action == 'update':
            # Обновяване на количество
            for item in cart:
                if item['product_id'] == product_id:
                    if quantity > 0:
                        item['quantity'] = quantity
                    else:
                        cart.remove(item)
                    break

        elif action == 'remove':
            # Премахване на продукт
            cart = [item for item in cart if item['product_id'] != product_id]

        request.session['cart'] = cart
        total = sum(item['price'] * item['quantity'] for item in cart)

        return JsonResponse({
            'success': True,
            'cart': cart,
            'total': total,
            'cart_count': sum(item['quantity'] for item in cart)
        })

    return JsonResponse({'error': 'Invalid request method'}, status=400)


# ========== СЪЗДАВАНЕ НА ПОРЪЧКА ОТ КОЛИЧКАТА ==========
def order_create(request):
    """Създаване на нова поръчка от количката"""

    # Вземаме количката от сесията
    cart = request.session.get('cart', [])

    # Проверка дали количката не е празна
    if not cart:
        messages.error(request, 'Количката е празна. Добавете продукти преди да направите поръчка.')
        return redirect('orders:cart')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)

        if form.is_valid():
            # 1. Записваме поръчката
            order = form.save(commit=False)

            # Ако потребителят е логнат, свързваме поръчката с него
            if request.user.is_authenticated:
                order.user = request.user
                # Попълваме имената и имейла от профила
                order.guest_name = request.user.get_full_name() or request.user.username
                order.guest_email = request.user.email

            order.save()

            # 2. Записваме артикулите от количката
            for item in cart:
                product = get_object_or_404(Product, id=item['product_id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price_at_time=product.price
                )

            # 3. Изчистване на количката след успешна поръчка
            if 'cart' in request.session:
                del request.session['cart']

            # 4. Актуализираме профила с въведения адрес и телефон, ако липсват
            if request.user.is_authenticated:
                user = request.user
                if not user.shipping_address and form.cleaned_data.get('shipping_address'):
                    user.shipping_address = form.cleaned_data['shipping_address']
                    user.save(update_fields=['shipping_address'])

                if not user.phone_number and form.cleaned_data.get('guest_phone'):
                    user.phone_number = form.cleaned_data['guest_phone']
                    user.save(update_fields=['phone_number'])

            messages.success(request, 'Благодарим за поръчката! Ще се свържем с вас.')
            return redirect('orders:order_detail', pk=order.id)
        else:
            # Показване на грешки
            messages.error(request, 'Моля, поправете грешките във формата.')
    else:
        # GET заявка – създаваме форма с предварително попълнени данни от потребителя
        initial_data = {}

        # Ако потребителят е логнат, опитваме се да вземем данните от профила му
        if request.user.is_authenticated:
            # Проверка за адрес - използваме shipping_address или address
            shipping_address = getattr(request.user, 'shipping_address', None) or getattr(request.user, 'address', None)
            if shipping_address:
                initial_data['shipping_address'] = shipping_address

            # Проверка за телефон - използваме phone_number (не phone)
            if hasattr(request.user, 'phone_number') and request.user.phone_number:
                initial_data['guest_phone'] = request.user.phone_number

        form = OrderCreateForm(initial=initial_data, request=request)

    # Изчисляваме общата сума за показване
    total = sum(item['price'] * item['quantity'] for item in cart)

    return render(request, 'orders/order_form.html', {
        'form': form,
        'cart': cart,
        'total': total,
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
