# core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Начална страница
    path('', views.home_view, name='index'),

    # Информационни страници
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    path('privacy/', views.privacy_policy_view, name='privacy'),
    path('terms/', views.terms_view, name='terms'),
]

