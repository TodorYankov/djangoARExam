# orders/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

from .models import Order, OrderItem
from .forms import OrderForm, OrderCreateForm, OrderItemFormSet, OrderStatusForm, OrderItemForm
from products.models import Product
from django.db.models import Q

# ========== ПУБЛИЧНА ФУНКЦИЯ ЗА СЪЗДАВАНЕ НА ПОРЪЧКА ==========
def order_create(request):
    if request.method == 'POST':
        # Създаваме формата за поръчка с POST данни
        form = OrderCreateForm(request.POST)
        # ВАЖНО: Използваме същия prefix ('items') както в шаблона и GET случая,
        # за да може Django да свърже полетата от заявката с formset-а.
        formset = OrderItemFormSet(request.POST, prefix='items')

        # --- ДЕБЪГ: извеждаме получените данни в конзолата ---
        print("=== POST данни от заявката ===")
        print(request.POST)
        print("--- Стойност на първия продукт (items-0-product) ---")
        print(request.POST.getlist('items-0-product'))  # ще покаже ID-то на избрания продукт

        # Проверяваме дали и двете форми са валидни
        if form.is_valid() and formset.is_valid():
            # 1. Записваме поръчката, за да получи ID
            order = form.save()

            # 2. Задаваме на formset-а към коя поръчка принадлежи (важно за запис)
            formset.instance = order

            # 3. Записваме артикулите без commit, за да добавим допълнителни данни
            items = formset.save(commit=False)
            for item in items:
                item.order = order  # вече би трябвало да е зададено, но за всеки случай
                # Взимаме актуалната цена от продукта, със защита при липсваща стойност
                item.price_at_time = item.product.price if item.product.price else 0
                item.save()

            # 4. Изтриваме маркираните за изтриване артикули (ако има такива)
            for item in formset.deleted_objects:
                item.delete()

            messages.success(request, 'Благодарим за поръчката! Ще се свържем с вас.')
            return redirect('products:product_list')
        else:
            # --- ДЕБЪГ: при невалидни данни показваме грешките в конзолата ---
            print("!!! Грешки във формата за поръчка !!!")
            print(form.errors)
            print("!!! Грешки във formset (по отделните редове) !!!")
            print(formset.errors)
            print("!!! Общи грешки на formset (независими от редовете) !!!")
            print(formset.non_form_errors())

            # Връщаме шаблона с формите и грешките, за да може да ги видите и в самата страница (временно)
            return render(request, 'orders/order_form.html', {
                'form': form,
                'formset': formset,
                'form_errors': form.errors,
                'formset_errors': formset.errors,
            })
    else:
        # GET заявка – показваме празна форма
        form = OrderCreateForm()
        # Създаваме празна поръчка (незаписана), за да генерираме празните редове за продукти
        empty_order = Order()
        formset = OrderItemFormSet(instance=empty_order, prefix='items')
        return render(request, 'orders/order_form.html', {
            'form': form,
            'formset': formset,
        })

# ========== ДОБАВЯНЕ В КОЛИЧКАТА (ОСТАВА НЕПРОМЕНЕНО) ==========
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Тук -> истинската логика за количката
    messages.success(request, f"{product.name} е добавен в количката.")  # product.title? В модела е name
    return redirect(request.META.get('HTTP_REFERER', 'products:product_list'))

# ========== КЛАСОВИ ИЗГЛЕДИ (АДМИН ЧАСТ) ==========
class OrderListView(ListView):
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
                queryset = queryset.filter(
                    Q(customer_name__icontains=search_query) |
                    Q(customer_email__icontains=search_query) |
                    Q(customer_phone__icontains=search_query)
                )

        return queryset.order_by('-created_at')


class OrderDetailView(DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('orders:order_list')

    def form_valid(self, form):
        # Мога да добавя имейл известия и др.
        return super().form_valid(form)


class OrderUpdateView(UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('orders:order_list')


class OrderDeleteView(DeleteView):
    model = Order
    template_name = 'orders/order_confirm_delete.html'
    success_url = reverse_lazy('orders:order_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Изтриване на поръчка #{self.object.id}"
        return context


class OrderStatusUpdateView(UpdateView):
    model = Order
    form_class = OrderStatusForm
    template_name = 'orders/order_status_form.html'
    success_url = reverse_lazy('orders:order_list')


class OrderItemCreateView(CreateView):
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
        return redirect('orders:order_detail', pk=order.id)

