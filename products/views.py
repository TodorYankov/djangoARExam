from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Product, Category, Brand
from .forms import ProductForm, CategoryForm


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        queryset = Product.objects.filter(is_available=True)

        # 1. Филтър по категория
        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # 2. Филтър по тип на продукт
        product_type = self.request.GET.get('type')
        if product_type:
            queryset = queryset.filter(product_type=product_type)

        # 3. Филтър по марка
        brand_id = self.request.GET.get('brand')
        if brand_id:
            queryset = queryset.filter(brand_id=brand_id)

        # 4. Филтър по минимална цена
        min_price = self.request.GET.get('min_price')
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except (ValueError, TypeError):
                pass  # Игнорираме грешни стойности

        # 5. Филтър по максимална цена
        max_price = self.request.GET.get('max_price')
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except (ValueError, TypeError):
                pass  # Игнорираме грешни стойности

        # 6. Филтър по наличност
        in_stock = self.request.GET.get('in_stock')
        if in_stock == 'yes':
            queryset = queryset.filter(stock_quantity__gt=0)
        elif in_stock == 'no':
            queryset = queryset.filter(stock_quantity=0)

        # 7. Търсене
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(brand__name__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )

        # 8. Сортиране
        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by in ['price', '-price', 'name', '-name', 'created_at', '-created_at', 'stock_quantity',
                       '-stock_quantity']:
            queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['brands'] = Brand.objects.all()
        context['product_types'] = Product.PRODUCT_TYPES

        # Създаване на речници за бърз достъп (заместват get_item филтъра)
        context['categories_dict'] = {str(cat.id): cat.name for cat in context['categories']}
        context['brands_dict'] = {str(brand.id): brand.name for brand in context['brands']}

        # Вземане на текущите филтри
        current_filters = {
            'category': self.request.GET.get('category', ''),
            'brand': self.request.GET.get('brand', ''),
            'type': self.request.GET.get('type', ''),
            'min_price': self.request.GET.get('min_price', ''),
            'max_price': self.request.GET.get('max_price', ''),
            'in_stock': self.request.GET.get('in_stock', ''),
            'search': self.request.GET.get('search', ''),
            'sort': self.request.GET.get('sort', '-created_at'),
        }
        context['current_filters'] = current_filters

        # Пряк достъп до имената за избраните филтри
        context['selected_category_name'] = context['categories_dict'].get(current_filters['category'], '')
        context['selected_brand_name'] = context['brands_dict'].get(current_filters['brand'], '')

        # Изчисляване на информация за филтрите
        context['total_products'] = Product.objects.filter(is_available=True).count()
        context['filtered_count'] = context['products'].count()

        # Вземане на display стойност за избрания тип
        selected_type_name = ''
        for type_id, type_name in Product.PRODUCT_TYPES:
            if current_filters['type'] == type_id:
                selected_type_name = type_name
                break
        context['selected_type_name'] = selected_type_name

        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Подобни продукти (от същата категория)
        context['related_products'] = Product.objects.filter(
            category=self.object.category,
            is_available=True
        ).exclude(id=self.object.id)[:4]
        return context


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        # Може да се добави допълнителна логика преди запазване
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавяне на нов продукт'
        context['submit_text'] = 'Създай продукт'
        return context


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактиране на "{self.object.name}"'
        context['submit_text'] = 'Запази промените'
        return context


class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Изтриване на продукт"
        context['object_name'] = self.object.name
        return context


class CategoryListView(ListView):
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'
    ordering = ['name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Всички категории'
        # Брой продукти във всяка категория
        for category in context['categories']:
            category.product_count = Product.objects.filter(category=category).count()
        return context


class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'products/category_form.html'
    success_url = reverse_lazy('category_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавяне на нова категория'
        context['submit_text'] = 'Създай категория'
        return context


class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'products/category_form.html'
    success_url = reverse_lazy('category_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактиране на категория "{self.object.name}"'
        context['submit_text'] = 'Запази промените'
        return context


class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'products/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Изтриване на категория"
        context['object_name'] = self.object.name
        # Проверка дали има продукти в категорията
        context['has_products'] = Product.objects.filter(category=self.object).exists()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Проверка дали има продукти в категорията
        if Product.objects.filter(category=self.object).exists():
            # Ако има продукти, не позволяваме изтриване
            return render(request, self.template_name, {
                'object': self.object,
                'title': f"Изтриване на категория",
                'object_name': self.object.name,
                'has_products': True,
                'error_message': 'Не можете да изтриете категория, която съдържа продукти!'
            })
        return super().post(request, *args, **kwargs)


class BrandListView(ListView):
    model = Brand
    template_name = 'products/brand_list.html'
    context_object_name = 'brands'
    ordering = ['name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Всички марки'
        # Брой продукти за всяка марка
        for brand in context['brands']:
            brand.product_count = Product.objects.filter(brand=brand).count()
        return context


# Допълнителни view-та ако са  нужни
def product_stats(request):
    """Статистика за продуктите"""
    total_products = Product.objects.count()
    available_products = Product.objects.filter(is_available=True).count()
    out_of_stock = Product.objects.filter(stock_quantity=0).count()

    # Продукти по категории
    products_by_category = {}
    for category in Category.objects.all():
        count = Product.objects.filter(category=category).count()
        if count > 0:
            products_by_category[category.name] = count

    # Продукти по марки
    products_by_brand = {}
    for brand in Brand.objects.all():
        count = Product.objects.filter(brand=brand).count()
        if count > 0:
            products_by_brand[brand.name] = count

    context = {
        'total_products': total_products,
        'available_products': available_products,
        'out_of_stock': out_of_stock,
        'products_by_category': products_by_category,
        'products_by_brand': products_by_brand,
    }

    return render(request, 'products/product_stats.html', context)


def export_products_csv(request):
    """Експорт на продукти в CSV формат"""
    import csv
    from django.http import HttpResponse

    # Създаване на HTTP response с CSV прикачен файл
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products_export.csv"'

    writer = csv.writer(response)
    # Заглавен ред
    writer.writerow(['ID', 'Име', 'Описание', 'Цена', 'Категория', 'Марка', 'Тип', 'Наличност', 'Създаден на'])

    # Данни
    products = Product.objects.all().select_related('category', 'brand')
    for product in products:
        writer.writerow([
            product.id,
            product.name,
            product.description[:100],  # Само първите 100 символа
            product.price,
            product.category.name if product.category else '',
            product.brand.name if product.brand else '',
            product.get_product_type_display(),
            product.stock_quantity,
            product.created_at.strftime('%d.%m.%Y %H:%M')
        ])

    return response

