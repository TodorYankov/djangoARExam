"""
settings.py
Django settings for djangoARExam project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!

# Зареди .env
load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Разрешени хостове
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '83.228.97.7']

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    # Celery apps
    'django_celery_beat',
    'django_celery_results',
    # Local apps
    'accounts',
    'core',
    'products',
    'orders',
    'reviews',
]

AUTH_USER_MODEL = 'accounts.CustomUser'

# Логин/Логаут пренасочвания
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:profile'
LOGOUT_REDIRECT_URL = 'core:index'

# Персонализирани страници за грешки
handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'djangoARExam.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'builtins': [
                'django.templatetags.static',
            ],
        },
    },
]

WSGI_APPLICATION = 'djangoARExam.wsgi.application'

# Database
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# PostgreSQL (разкоментиран и готов за production)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "djangoARExam",
        "USER": "postgres",
        "PASSWORD": "123456789",
        "HOST": "localhost",
        "PORT": "5432",
    }
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'bg'
TIME_ZONE = 'Europe/Sofia'
USE_I18N = True
USE_TZ = True

# Формати на дата
DATE_INPUT_FORMATS = ['%d.%m.%Y', '%Y-%m-%d']
DATE_FORMAT = 'd.m.Y'
DATETIME_FORMAT = 'd.m.Y H:i'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Email settings (за разработка - използва конзолата)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# За production използвайте SMTP:
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your-email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your-app-password'
# DEFAULT_FROM_EMAIL = 'TechShop <noreply@techshop.bg>'

# ========== CELERY CONFIGURATION ==========
# Определяне на средата
ENVIRONMENT = os.environ.get('DJANGO_ENV', 'development')

if ENVIRONMENT == 'production':
    # Production settings (за Xubuntu)
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
    CELERY_TASK_ALWAYS_EAGER = False

    # Redis Cache Configuration (за production)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': 'redis://localhost:6379/1',
            'TIMEOUT': 300,
        }
    }
else:
    # Development settings (за Windows)
    CELERY_TASK_ALWAYS_EAGER = True  # Задачите се изпълняват синхронно
    CELERY_BROKER_URL = 'memory://'
    CELERY_RESULT_BACKEND = 'cache+memory://'

    # SQLite Cache за разработка (ако не искате Redis)
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }

# Общи Celery настройки (за всички среди)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_RESULT_EXTENDED = True
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 20 * 60  # 20 minutes
CELERY_TASK_EAGER_PROPAGATES = True

# REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
}

# За да работи локализацията на български
import locale
import sys

# Опит за зареждане на българска локализация
try:
    locale.setlocale(locale.LC_TIME, 'bg_BG.UTF-8')
except locale.Error:
    # Проверка дали сме в development среда
    from django.conf import settings

    if settings.DEBUG:
        # Показваме инструкции само в development
        print("\n" + "=" * 70)
        print("⚠️  БЪЛГАРСКАТА ЛОКАЛИЗАЦИЯ НЕ Е ИНСТАЛИРАНА")
        print("=" * 70)
        print("\nЗа да инсталирате българска локализация:")
        print("\n📌 За Ubuntu/Debian:")
        print("   sudo apt-get install language-pack-bg")
        print("\n📌 За Windows:")
        print("   - Отворете Control Panel")
        print("   - Region → Administrative → Change system locale")
        print("   - Изберете 'Bulgarian (Bulgaria)'")
        print("   - Рестартирайте компютъра")
        print("\n📌 За Mac:")
        print("   locale-gen bg_BG.UTF-8")
        print("\n🔧 За момента се използва английска локализация\n")
    else:
        # В production - само лог
        import logging

        logging.warning("Bulgarian locale not available, using English")

    # Използваме системната локализация като fallback
    locale.setlocale(locale.LC_TIME, '')
