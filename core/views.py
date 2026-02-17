# core/views.py
from django.shortcuts import render
from products.models import Product
from django.views.generic import TemplateView


def home_view(request):
    """Начална страница"""
    latest_products = Product.objects.filter(is_available=True).order_by('-created_at')[:4]
    context = {
        'latest_products': latest_products,
    }
    return render(request, 'index.html', context)


def about_view(request):
    """Страница 'За нас'"""
    return render(request, 'core/about.html', {
        'title': 'За нас',
        'page_title': 'За TechShop'
    })


def contact_view(request):
    """Контактна страница"""
    return render(request, 'core/contact.html', {
        'title': 'Контакти',
        'page_title': 'Свържете се с нас'
    })


def privacy_policy_view(request):
    """Политика за поверителност"""
    return render(request, 'core/privacy.html', {
        'title': 'Политика за поверителност',
        'page_title': 'Политика за поверителност'
    })


def terms_view(request):
    """Общи условия"""
    return render(request, 'core/terms.html', {
        'title': 'Общи условия',
        'page_title': 'Общи условия за ползване'
    })


def custom_404(request, exception):
    """Персонализирана 404 страница"""
    return render(request, 'core/404.html', {
        'title': 'Страницата не е намерена',
        'page_title': '404 - Страницата не е намерена'
    }, status=404)


def custom_500(request):
    """Персонализирана 500 страница (опционално)"""
    return render(request, 'core/500.html', {
        'title': 'Вътрешна грешка в сървъра',
        'page_title': '500 - Вътрешна грешка'
    }, status=500)


# Class-Based View пример (за демонстрация)
class FAQView(TemplateView):
    """Често задавани въпроси (Class-Based View)"""
    template_name = 'core/faq.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'ЧЗВ'
        context['page_title'] = 'Често задавани въпроси'
        context['faqs'] = [
            {
                'question': 'Как мога да направя поръчка?',
                'answer': 'Можете да направите поръчка чрез формата за поръчки или да се свържете с нас.'
            },
            {
                'question': 'Какво е времето за доставка?',
                'answer': 'Доставката е в рамките на 1-3 работни дни за София и 2-5 за страната.'
            },
            {
                'question': 'Имате ли гаранция?',
                'answer': 'Да, всички продукти имат гаранция от 24 месеца.'
            },
        ]
        return context


