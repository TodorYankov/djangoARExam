# products/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from django.urls import reverse_lazy
from .models import Product, Category
from .forms import ProductForm, CategoryForm


def product_create(request):
    # Проверка за категории
    categories_exist = Category.objects.exists()

    # АКО НЯМА КАТЕГОРИИ И ТОВА Е GET ЗАЯВКА - показваме предупреждение
    if not categories_exist and request.method == 'GET':
        messages.warning(request, '⚠️ ВНИМАНИЕ: Няма създадени категории! Първо трябва да създадете категория.')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, 'Продуктът е създаден успешно!')
            return redirect('products:product_detail', pk=product.pk)
    else:
        form = ProductForm()

    context = {
        'form': form,
        'no_categories': not categories_exist,
        'categories_exist': categories_exist,
        'title': 'Създаване на нов продукт',
        'submit_text': 'Създай продукт',
    }
    return render(request, 'products/product_form.html', context)


def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    categories_exist = Category.objects.exists()

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Продуктът е обновен успешно!')
            return redirect('products:product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)

    context = {
        'form': form,
        'product': product,
        'no_categories': not categories_exist,
        'categories_exist': categories_exist,
        'title': f'Редактиране на {product.name}',
        'submit_text': 'Запази промените',
    }
    return render(request, 'products/product_form.html', context)


def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    categories_exist = Category.objects.exists()

    if product.stock_quantity == 0:
        messages.warning(request, 'Продукт с 0 наличност е маркиран като изчерпан')

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Продуктът беше успешно обновен')
            return redirect('products:product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)

    return render(request, 'products/product_form.html', {
        'form': form,
        'product': product,
        'no_categories': not categories_exist,
        'categories_exist': categories_exist,
        'title': f'Редактиране на {product.name}',
        'submit_text': 'Запази промените',
    })


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 9

    def get_queryset(self):
        queryset = Product.objects.filter(is_available=True)

        # 1. Филтър по категория (променено да работи със slug)
        category_slug = self.request.GET.get('category')
        if category_slug:
            try:
                # Намираме категорията по slug
                category = Category.objects.get(slug=category_slug)
                queryset = queryset.filter(category=category)
            except Category.DoesNotExist:
                # Ако категорията не съществува, връщаме празен резултат
                return queryset.none()

        # 2. Филтър по тип на продукт
        product_type = self.request.GET.get('type')
        if product_type:
            queryset = queryset.filter(product_type=product_type)

        # 3. Филтър по марка

        # 4. Филтър по минимална цена
        min_price = self.request.GET.get('min_price')
        if min_price:
            try:
                queryset = queryset.filter(price__gte=float(min_price))
            except (ValueError, TypeError):
                pass

        # 5. Филтър по максимална цена
        max_price = self.request.GET.get('max_price')
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except (ValueError, TypeError):
                pass

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
        context['product_types'] = Product.PRODUCT_TYPES

        # Създаване на речници за бърз достъп (slug -> име)
        context['categories_dict'] = {cat.slug: cat.name for cat in context['categories']}

        # Вземане на текущите филтри
        current_filters = {
            'category': self.request.GET.get('category', ''),
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
    success_url = reverse_lazy('products:product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories_exist = Category.objects.exists()
        context['title'] = 'Добавяне на нов продукт'
        context['submit_text'] = 'Създай продукт'
        context['no_categories'] = not categories_exist
        context['categories_exist'] = categories_exist

        # Добавяне на предупреждение
        if not categories_exist:
            messages.warning(self.request,
                             '⚠️ ВНИМАНИЕ: Няма създадени категории! Първо трябва да създадете категория.')

        return context

    def form_valid(self, form):
        if not Category.objects.exists():
            messages.error(self.request, '❌ Не можете да създадете продукт без категория!')
            return redirect('products:product_create')

        response = super().form_valid(form)
        messages.success(self.request, f'Продукт "{self.object.name}" беше създаден успешно')
        return response


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories_exist = Category.objects.exists()
        context['title'] = f'Редактиране на "{self.object.name}"'
        context['submit_text'] = 'Запази промените'
        context['no_categories'] = not categories_exist
        context['categories_exist'] = categories_exist
        return context

    def get_success_url(self):
        messages.success(self.request, f'Продукт "{self.object.name}" беше обновен успешно')
        return reverse_lazy('products:product_detail', kwargs={'pk': self.object.pk})


class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'products/product_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Изтриване на продукт"
        context['object_name'] = self.object.name
        return context

    def get_success_url(self):
        messages.success(self.request, 'Продуктът беше изтрит успешно')
        return reverse_lazy('products:product_list')


class CategoryListView(ListView):
    model = Category
    template_name = 'products/category_list.html'
    context_object_name = 'categories'
    ordering = ['name']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Всички категории'

        # Брой продукти във всяка категория и изчисляване на статистики
        total_products = 0
        max_products = 0

        for category in context['categories']:
            count = Product.objects.filter(category=category).count()
            category.product_count = count  # Запазваме за шаблона
            total_products += count
            if count > max_products:
                max_products = count

        # Добави статистиките в контекста
        context['total_products'] = total_products
        context['max_products'] = max_products

        # Топ 3 категории с най-много продукти
        top_categories = sorted(
            context['categories'],
            key=lambda cat: cat.product_count,
            reverse=True
        )[:3]
        context['top_categories'] = top_categories

        return context


class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'products/category_form.html'
    success_url = reverse_lazy('products:category_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавяне на нова категория'
        context['submit_text'] = 'Създай категория'
        return context


class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'products/category_form.html'
    success_url = reverse_lazy('products:category_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактиране на категория "{self.object.name}"'
        context['submit_text'] = 'Запази промените'
        return context


class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'products/category_confirm_delete.html'
    success_url = reverse_lazy('products:category_list')

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


def export_products_csv(request):
    """Експорт на продукти в CSV формат"""
    import csv
    from django.http import HttpResponse

    # Създаване на HTTP response с CSV прикачен файл
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="products_export.csv"'

    writer = csv.writer(response)
    # Заглавен ред
    writer.writerow(['ID', 'Име', 'Описание', 'Цена', 'Категория', 'Тип', 'Наличност', 'Създаден на'])

    # Данни
    products = Product.objects.all().select_related('category')
    for product in products:
        writer.writerow([
            product.id,
            product.name,
            product.description[:100],  # Само първите 100 символа
            product.price,
            product.category.name if product.category else '',
            product.get_product_type_display(),
            product.stock_quantity,
            product.created_at.strftime('%d.%m.%Y %H:%M')
        ])

    return response

