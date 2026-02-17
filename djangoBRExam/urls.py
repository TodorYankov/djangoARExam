# urls.py (главният файл на проекта)
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

# Не импортирам home_view директно, ще го взема от core.urls

urlpatterns = [
    path('admin/', admin.site.urls),

    # Включвам core.urls под root ('')
    # (тогава всички core страници ще са в корена на сайта)
    path('', include('core.urls')),

    path('products/', include('products.urls')),
    path('orders/', include('orders.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Персонализирана 404 страница
handler404 = 'core.views.custom_404'



