# orders/views.py
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, F, DecimalField, ExpressionWrapper
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import OrderForm, OrderCreateForm, OrderStatusForm, OrderItemForm
from .models import Order, OrderItem
from products.models import Product, Category


def get_orders_statistics():
    """Обща статистика за поръчките"""
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()

    total_expr = ExpressionWrapper(
        F('quantity') * F('price_at_time'),
        output_field=DecimalField(max_digits=12, decimal_places=2)
    )

    total_revenue = OrderItem.objects.aggregate(
        total=Sum(total_expr)
    )['total'] or 0

    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

    return {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
        'avg_order_value': avg_order_value,
    }


def statistics_api(request):
    """API за статистика на поръчките (AJAX)"""
    stats = get_orders_statistics()

    return JsonResponse({
        'total_orders': stats['total_orders'],
        'pending_orders': stats['pending_orders'],
        'total_revenue': float(stats['total_revenue']),
        'avg_order_value': float(stats['avg_order_value']),
    })


# ========== ФУНКЦИИ ЗА КОЛИЧКАТА ==========
@login_required
def cart_view(request):
    """Преглед на количката"""
    cart = request.session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart)
    cart_count = sum(item['quantity'] for item in cart)

    # Вземи първите 3 категории (сортирани по ID - първо създадените)
    popular_categories = Category.objects.all().order_by('id')[:3]

    context = {
        'cart': cart,
        'total': total,
        'cart_count': cart_count,
        'popular_categories': popular_categories,  # Добавено за динамичните бутони
    }
    return render(request, 'orders/cart.html', context)


@login_required
def update_cart_item(request, product_id):
    """Обновява количество на продукт в количката"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=400)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Invalid quantity'}, status=400)

    cart = request.session.get('cart', [])

    for item in cart:
        if item['product_id'] == product_id:
            if quantity > 0:
                item['quantity'] = quantity
            else:
                cart.remove(item)
            break

    request.session['cart'] = cart
    request.session.modified = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': sum(item['quantity'] for item in cart),
            'total': sum(item['price'] * item['quantity'] for item in cart),
        })

    messages.success(request, 'Количеството беше обновено успешно.')
    return redirect('orders:cart')


@login_required
def remove_from_cart(request, product_id):
    """Премахва продукт от количката"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=400)

    cart = request.session.get('cart', [])
    cart = [item for item in cart if item['product_id'] != product_id]

    request.session['cart'] = cart
    request.session.modified = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': sum(item['quantity'] for item in cart),
            'total': sum(item['price'] * item['quantity'] for item in cart),
        })

    messages.success(request, 'Продуктът беше премахнат от количката.')
    return redirect('orders:cart')


@login_required
def add_to_cart(request, product_id):
    """Добавя продукт в количката (сесия) - с поддръжка на AJAX"""
    product = get_object_or_404(Product, id=product_id, is_available=True)

    quantity = 1
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            data = json.loads(request.body)
            quantity = int(data.get('quantity', 1))
        except (json.JSONDecodeError, TypeError, ValueError):
            quantity = 1

    quantity = max(1, quantity)

    if 'cart' not in request.session:
        request.session['cart'] = []

    cart = request.session['cart']

    found = False
    for item in cart:
        if item['product_id'] == product_id:
            item['quantity'] += quantity
            found = True
            break

    if not found:
        cart.append({
            'product_id': product.id,
            'name': product.name,
            'price': float(product.price),
            'quantity': quantity,
            'image': product.image.url if product.image else None,
        })

    request.session['cart'] = cart
    request.session.modified = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': sum(item['quantity'] for item in cart),
            'total': sum(item['price'] * item['quantity'] for item in cart),
            'message': f'{product.name} беше добавен в количката!',
        })

    messages.success(request, f'{product.name} беше добавен в количката!')
    return redirect(request.META.get('HTTP_REFERER', 'products:product_list'))


def cart_api(request):
    """API endpoint за количката (AJAX) - публичен достъп"""
    if not request.user.is_authenticated:
        return JsonResponse({
            'cart': [],
            'total': 0,
            'cart_count': 0,
        })

    if request.method == 'GET':
        cart = request.session.get('cart', [])
        total = sum(item['price'] * item['quantity'] for item in cart)
        return JsonResponse({
            'cart': cart,
            'total': total,
            'cart_count': sum(item['quantity'] for item in cart),
        })

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except (json.JSONDecodeError, TypeError):
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

        action = data.get('action')
        product_id = data.get('product_id')

        try:
            quantity = int(data.get('quantity', 1))
        except (TypeError, ValueError):
            quantity = 1

        quantity = max(1, quantity)
        cart = request.session.get('cart', [])

        if action == 'add':
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
                    'image': product.image.url if product.image else None,
                })

        elif action == 'update':
            for item in cart:
                if item['product_id'] == product_id:
                    if quantity > 0:
                        item['quantity'] = quantity
                    else:
                        cart.remove(item)
                    break

        elif action == 'remove':
            cart = [item for item in cart if item['product_id'] != product_id]

        else:
            return JsonResponse({'success': False, 'error': 'Invalid action'}, status=400)

        request.session['cart'] = cart
        request.session.modified = True

        total = sum(item['price'] * item['quantity'] for item in cart)

        return JsonResponse({
            'success': True,
            'cart': cart,
            'total': total,
            'cart_count': sum(item['quantity'] for item in cart),
        })

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def order_create(request):
    """Създаване на нова поръчка от количката"""
    cart = request.session.get('cart', [])

    if not cart:
        messages.error(request, 'Количката е празна. Добавете продукти преди да направите поръчка.')
        return redirect('orders:cart')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)

        if form.is_valid():
            order = form.save(commit=False)

            if request.user.is_authenticated:
                order.user = request.user
                order.guest_name = request.user.get_full_name() or request.user.username
                order.guest_email = request.user.email

            order.save()

            for item in cart:
                product = get_object_or_404(Product, id=item['product_id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price_at_time=product.price
                )

            if 'cart' in request.session:
                del request.session['cart']
                request.session.modified = True

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

        messages.error(request, 'Моля, поправете грешките във формата.')
    else:
        initial_data = {}

        if request.user.is_authenticated:
            shipping_address = getattr(request.user, 'shipping_address', None) or getattr(request.user, 'address', None)
            if shipping_address:
                initial_data['shipping_address'] = shipping_address

            if hasattr(request.user, 'phone_number') and request.user.phone_number:
                initial_data['guest_phone'] = request.user.phone_number

        form = OrderCreateForm(initial=initial_data, request=request)

    total = sum(item['price'] * item['quantity'] for item in cart)

    return render(request, 'orders/order_form.html', {
        'form': form,
        'cart': cart,
        'total': total,
    })


# ========== КЛАСОВИ ИЗГЛЕДИ ==========
class OrderListView(ListView):
    """Списък с поръчки със статистика"""
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        queryset = Order.objects.all()

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        search_query = self.request.GET.get('search')
        if search_query:
            if search_query.isdigit():
                queryset = queryset.filter(id=int(search_query))
            else:
                queryset = queryset.filter(
                    Q(user__first_name__icontains=search_query) |
                    Q(user__last_name__icontains=search_query) |
                    Q(user__username__icontains=search_query) |
                    Q(user__email__icontains=search_query) |
                    Q(guest_name__icontains=search_query) |
                    Q(guest_email__icontains=search_query) |
                    Q(guest_phone__icontains=search_query)
                )

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        stats = get_orders_statistics()
        context['total_orders'] = stats['total_orders']
        context['pending_orders'] = stats['pending_orders']
        context['total_revenue'] = stats['total_revenue']
        context['avg_order_value'] = stats['avg_order_value']

        return context


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

