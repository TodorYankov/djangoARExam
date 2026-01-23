from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Order, OrderItem
from .forms import OrderForm, OrderStatusForm, OrderItemForm
from products.models import Product


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
            queryset = queryset.filter(
                Q(customer_name__icontains=search_query) |
                Q(customer_email__icontains=search_query) |
                Q(id__icontains=search_query)
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
    success_url = reverse_lazy('order_list')

    def form_valid(self, form):
        # Мога да добавя имейл известия и др.
        return super().form_valid(form)


class OrderUpdateView(UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'orders/order_form.html'
    success_url = reverse_lazy('order_list')


class OrderDeleteView(DeleteView):
    model = Order
    template_name = 'orders/order_confirm_delete.html'
    success_url = reverse_lazy('order_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Изтриване на поръчка #{self.object.id}"
        return context


class OrderStatusUpdateView(UpdateView):
    model = Order
    form_class = OrderStatusForm
    template_name = 'orders/order_status_form.html'
    success_url = reverse_lazy('order_list')


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
        return redirect('order_detail', pk=order.id)



