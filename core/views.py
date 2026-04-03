# core/views.py
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.template import loader
from django.http import JsonResponse, HttpResponse
from products.models import Product
from .forms import ContactForm, NewsletterForm


def home_view(request):
    """Начална страница"""
    # Проверка дали моделът има поле is_available
    if hasattr(Product, 'is_available'):
        latest_products = Product.objects.filter(is_available=True).order_by('-created_at')[:4]
    else:
        latest_products = Product.objects.all().order_by('-id')[:4]

    context = {
        'latest_products': latest_products,
        'newsletter_form': NewsletterForm(),
    }

    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Тук добавете логика за запазване на имейла
            messages.success(request, 'Успешно се абонирахте за нашия бюлетин!')
        else:
            messages.error(request, 'Моля, въведете валиден имейл адрес.')
        return redirect('core:index')

    return render(request, 'index.html', context)


def about_view(request):
    """Страница 'За нас'"""
    return render(request, 'core/about.html')


def contact_view(request):
    """Контактна страница"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Запазване на съобщението (ако има модел ContactMessage)
            # contact = form.save()
            messages.success(request, 'Вашето съобщение беше изпратено успешно! Ще се свържем с вас скоро.')

            # Изпращане на имейл (опционално)
            try:
                send_mail(
                    f'Ново съобщение от {form.cleaned_data["name"]}',
                    form.cleaned_data['message'],
                    form.cleaned_data['email'],
                    [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
            except:
                pass

            return redirect('core:contact')
        else:
            messages.error(request, 'Моля, поправете грешките във формата.')
    else:
        form = ContactForm()

    return render(request, 'core/contact.html', {'form': form})


def privacy_policy_view(request):
    """Политика за поверителност"""
    return render(request, 'core/privacy.html')


def terms_view(request):
    """Общи условия"""
    return render(request, 'core/terms.html')


def custom_404(request, exception):
    """Персонализирана 404 страница"""
    template = loader.get_template('core/404.html')
    context = {
        'title': 'Страницата не е намерена',
        'message': 'Страницата, която търсите, не съществува или е премахната.',
    }

    # Проверка дали заявката е за API
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Not Found',
            'message': 'The requested resource was not found.',
            'status_code': 404
        }, status=404)

    return HttpResponse(template.render(context, request), status=404)


def custom_500(request):
    """Персонализирана 500 страница"""
    template = loader.get_template('core/500.html')
    context = {
        'title': 'Вътрешна грешка на сървъра',
        'message': 'Възникна проблем при обработката на заявката. Моля, опитайте по-късно.',
    }

    # Проверка дали заявката е за API
    if request.path.startswith('/api/'):
        return JsonResponse({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred. Please try again later.',
            'status_code': 500
        }, status=500)

    return HttpResponse(template.render(context, request), status=500)


class FAQView(TemplateView):
    """Често задавани въпроси (Class-Based View)"""
    template_name = 'core/faq.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
            {
                'question': 'Какви са начините на плащане?',
                'answer': 'Приемаме плащане с наложен платеж, банков превод и кредитна/дебитна карта.'
            },
            {
                'question': 'Мога ли да върна продукт?',
                'answer': 'Да, имате право да върнете продукт в срок от 14 дни от получаването му.'
            },
        ]
        return context


