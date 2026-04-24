# orders/views.py
import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Sum, F, DecimalField, ExpressionWrapper
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .forms import OrderForm, OrderCreateForm, OrderStatusForm, OrderItemForm, OrderFormForUser, OrderFormForStaff
from .models import Order, OrderItem
from products.models import Product, Category


def get_user_orders_statistics(user):
    """Статистика само за конкретен потребител"""
    user_orders = Order.objects.filter(user=user)
    total_orders = user_orders.count()
    pending_orders = user_orders.filter(status='pending').count()

    # Използваме total_amount от базата данни
    total_revenue = user_orders.aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

    return {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
        'avg_order_value': avg_order_value,
    }


def get_all_orders_statistics():
    """Обща статистика за всички поръчки (само за staff)"""
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status='pending').count()

    total_revenue = Order.objects.aggregate(
        total=Sum('total_amount')
    )['total'] or 0

    avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

    return {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'total_revenue': total_revenue,
        'avg_order_value': avg_order_value,
    }


@staff_member_required
def statistics_api(request):
    """API за статистика на поръчките (AJAX) - САМО ЗА STAFF"""
    stats = get_all_orders_statistics()

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

    # Изчисляване на обща сума за всеки продукт и общо за количката
    for item in cart:
        item['total'] = item['price'] * item['quantity']

    total = sum(item['total'] for item in cart)
    cart_count = sum(item['quantity'] for item in cart)

    # Вземи първите 3 категории (сортирани по ID - първо създадените)
    popular_categories = Category.objects.all().order_by('id')[:3]

    context = {
        'cart': cart,
        'total': total,
        'cart_count': cart_count,
        'popular_categories': popular_categories,
    }
    return render(request, 'orders/cart.html', context)


@login_required
def update_cart_item(request, product_id):
    """Обновява количество на продукт в количката - ФИКСИРАНА ВЕРСИЯ"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Invalid method'}, status=400)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'error': 'Invalid quantity'}, status=400)

    cart = request.session.get('cart', [])
    item_found = False

    for i, item in enumerate(cart):
        if item['product_id'] == product_id:
            if quantity > 0:
                cart[i]['quantity'] = quantity
                cart[i]['total'] = cart[i]['price'] * quantity
                item_found = True
            else:
                cart.pop(i)
                item_found = True
            break

    if not item_found:
        return JsonResponse({'success': False, 'error': 'Product not found in cart'}, status=404)

    request.session['cart'] = cart
    request.session.modified = True

    # Изчисляваме новата обща сума
    new_total = sum(item['price'] * item['quantity'] for item in cart)
    new_cart_count = sum(item['quantity'] for item in cart)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': new_cart_count,
            'total': float(new_total),
            'item_total': float(cart[i]['total']) if item_found and quantity > 0 else 0,
            'quantity': quantity
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

    new_total = sum(item['price'] * item['quantity'] for item in cart)
    new_cart_count = sum(item['quantity'] for item in cart)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': new_cart_count,
            'total': float(new_total),
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
            item['total'] = item['price'] * item['quantity']
            found = True
            break

    if not found:
        cart.append({
            'product_id': product.id,
            'name': product.name,
            'price': float(product.price),
            'quantity': quantity,
            'total': float(product.price) * quantity,
            'image': product.image.url if product.image else None,
        })

    request.session['cart'] = cart
    request.session.modified = True

    new_total = sum(item['price'] * item['quantity'] for item in cart)
    new_cart_count = sum(item['quantity'] for item in cart)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_count': new_cart_count,
            'total': float(new_total),
            'message': f'{product.name} беше добавен в количката!',
        })

    messages.success(request, f'{product.name} беше добавен в количката!')
    return redirect(request.META.get('HTTP_REFERER', 'products:product_list'))


def cart_api(request):
    """API endpoint за количката (AJAX) - с правилна защита"""

    if request.method == 'GET':
        # Публичен GET - връща количката само ако потребителят е логнат
        if not request.user.is_authenticated:
            return JsonResponse({
                'cart': [],
                'total': 0,
                'cart_count': 0,
            })

        cart = request.session.get('cart', [])
        total = sum(item['price'] * item['quantity'] for item in cart)
        return JsonResponse({
            'cart': cart,
            'total': float(total),
            'cart_count': sum(item['quantity'] for item in cart),
        })

    if request.method == 'POST':
        # POST изисква автентикация
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Login required'}, status=401)

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
                    item['total'] = item['price'] * item['quantity']
                    found = True
                    break

            if not found:
                product = get_object_or_404(Product, id=product_id)
                cart.append({
                    'product_id': product.id,
                    'name': product.name,
                    'price': float(product.price),
                    'quantity': quantity,
                    'total': float(product.price) * quantity,
                    'image': product.image.url if product.image else None,
                })

        elif action == 'update':
            for i, item in enumerate(cart):
                if item['product_id'] == product_id:
                    if quantity > 0:
                        cart[i]['quantity'] = quantity
                        cart[i]['total'] = cart[i]['price'] * quantity
                    else:
                        cart.pop(i)
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
            'total': float(total),
            'cart_count': sum(item['quantity'] for item in cart),
        })

    return JsonResponse({'error': 'Invalid request method'}, status=400)


@login_required
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

            # Първо запазваме, за да имаме ID
            order.save()

            # Изчисляване на обща сума на поръчката
            total_amount = 0
            for item in cart:
                product = get_object_or_404(Product, id=item['product_id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price_at_time=product.price
                )
                total_amount += product.price * item['quantity']

            # Обновяваме total_amount в поръчката
            order.total_amount = total_amount
            order.save(update_fields=['total_amount'])

            # Изчистване на количката
            if 'cart' in request.session:
                del request.session['cart']
                request.session.modified = True

            # Запазване на адреса и телефона в профила, ако липсват
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


# ========== КЛАСОВИ ИЗГЛЕДИ СЪС ЗАЩИТА ==========

class OrderListView(LoginRequiredMixin, ListView):
    """Списък с поръчки - само за автентикирани потребители"""
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        # Ако е staff, вижда всички поръчки
        if self.request.user.is_staff:
            queryset = Order.objects.all()
        else:
            # Обикновен потребител - само своите поръчки
            queryset = Order.objects.filter(user=self.request.user)

        # Филтри по статус
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        # Търсене
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

        # Важно: Статистиката зависи от ролята на потребителя
        if self.request.user.is_staff:
            stats = get_all_orders_statistics()
        else:
            stats = get_user_orders_statistics(self.request.user)

        context['total_orders'] = stats['total_orders']
        context['pending_orders'] = stats['pending_orders']
        context['total_revenue'] = stats['total_revenue']
        context['avg_order_value'] = stats['avg_order_value']

        # Заглавие в зависимост от ролята
        if self.request.user.is_staff:
            context['title'] = 'Управление на поръчки'
        else:
            context['title'] = 'Моите поръчки'

        return context


class OrderDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """Детайли на поръчка - само за собственика или staff"""
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'

    def test_func(self):
        order = self.get_object()
        # Позволява на staff и на собственика на поръчката
        return self.request.user.is_staff or self.request.user == order.user


class OrderCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Създаване на поръчка (административно) - само за staff"""
    model = Order
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('orders:order_list')

    def test_func(self):
        return self.request.user.is_staff

    def get_form_class(self):
        """Използва формата за staff (с пълен достъп)"""
        return OrderFormForStaff

    def form_valid(self, form):
        order = form.save(commit=False)

        # Ако няма user, опитваме да намерим по имейл
        if not order.user and order.guest_email:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(email=order.guest_email)
                order.user = user
            except User.DoesNotExist:
                pass

        response = super().form_valid(form)
        messages.success(self.request, f'Поръчка #{order.id} беше създадена успешно')
        return response


class OrderUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактиране на поръчка - само за staff"""
    model = Order
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('orders:order_list')

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        """Допълнителна защита"""
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.none()

    def get_form_class(self):
        """Връща различна форма в зависимост от потребителя"""
        if self.request.user.is_staff:
            return OrderFormForStaff  # Администраторите виждат всички полета (включително статус)
        return OrderFormForUser  # Обикновените потребители НЕ виждат статус

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['order_items'] = self.object.items.all()
        context['order_total'] = self.object.total_amount
        context['is_staff_view'] = self.request.user.is_staff
        return context

    def form_valid(self, form):
        response = super().form_valid(form)

        if self.request.user.is_staff:
            messages.success(self.request, f'Поръчка #{self.object.id} беше обновена успешно')
        else:
            messages.success(self.request, 'Вашата поръчка беше обновена успешно')

        return response


class OrderDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Изтриване на поръчка - само за staff"""
    model = Order
    template_name = 'orders/order_confirm_delete.html'
    success_url = reverse_lazy('orders:order_list')

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Изтриване на поръчка #{self.object.id}"
        return context


class OrderStatusUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Обновяване на статуса на поръчка - само за staff"""
    model = Order
    form_class = OrderStatusForm
    template_name = 'orders/order_status_form.html'
    success_url = reverse_lazy('orders:order_list')

    def test_func(self):
        return self.request.user.is_staff


class OrderItemCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """Добавяне на артикул към поръчка - само за staff"""
    model = OrderItem
    form_class = OrderItemForm
    template_name = 'orders/orderitem_form.html'

    def test_func(self):
        return self.request.user.is_staff

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

        # Обновяване на общата сума на поръчката
        order.total_amount = order.items.aggregate(
            total=Sum(F('quantity') * F('price_at_time'))
        )['total'] or 0
        order.save(update_fields=['total_amount'])

        messages.success(self.request, f'Артикулът {order_item.product.name} беше добавен към поръчката.')
        return redirect('orders:order_detail', pk=order.id)
