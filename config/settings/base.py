"""
Base settings for Hospital Management System.
Compliant with Cameroon Law n°2010/012 on Health Personal Data Protection.
"""
from pathlib import Path
import os
import environ
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['127.0.0.1', 'localhost']),
    TIME_ZONE=(str, 'Africa/Douala'),
    LANGUAGE_CODE=(str, 'fr'),
    DATABASE_URL=(str, f"sqlite:///{BASE_DIR / 'db.sqlite3'}"),
    REDIS_URL=(str, 'redis://127.0.0.1:6379/1'),
    CELERY_BROKER_URL=(str, 'redis://127.0.0.1:6379/0'),
    ORANGE_MONEY_ENV=(str, 'sandbox'),
    MTN_MOMO_ENV=(str, 'sandbox'),
)

# Read .env if it exists
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env('SECRET_KEY', default='django-insecure-hospital-system-dev-key-2026-douala')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    'simple_history',
    'django_otp',
    'django_otp.plugins.otp_totp',
]

LOCAL_APPS = [
    'apps.core',
    'apps.accounts',
    'apps.patients',
    'apps.appointments',
    'apps.consultations',
    'apps.pharmacy',
    'apps.laboratory',
    'apps.rooms',
    'apps.billing',
    'apps.notifications',
    'apps.api',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # i18n
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',        # 2FA
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',  # Audit log
]

ROOT_URLCONF = 'config.urls'

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
                'django.template.context_processors.i18n',
                'apps.core.context_processors.hospital_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database configuration
DATABASES = {
    'default': env.db('DATABASE_URL', default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}")
}

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 10},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Authentication URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'core:dashboard'
LOGOUT_REDIRECT_URL = 'accounts:login'

# Internationalization & Localization
LANGUAGE_CODE = 'fr'
TIME_ZONE = 'Africa/Douala'
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ('fr', _('Français')),
    ('en', _('English')),
]

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Celery Configuration
CELERY_BROKER_URL = env('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = env.str('CELERY_RESULT_BACKEND', default=CELERY_BROKER_URL)
CELERY_TIMEZONE = TIME_ZONE
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Cache Configuration
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': env('REDIS_URL'),
    }
}

# Cameroon Mobile Money Integration Settings
ORANGE_MONEY = {
    'ENV': env('ORANGE_MONEY_ENV', default='sandbox'),
    'CLIENT_ID': env('ORANGE_MONEY_CLIENT_ID', default=''),
    'CLIENT_SECRET': env('ORANGE_MONEY_CLIENT_SECRET', default=''),
    'MERCHANT_KEY': env('ORANGE_MONEY_MERCHANT_KEY', default=''),
    'NOTIFICATION_URL': env('ORANGE_MONEY_NOTIFICATION_URL', default='http://localhost:8000/billing/webhook/orange-money/'),
    'CURRENCY': 'XAF',
}

MTN_MOMO = {
    'ENV': env('MTN_MOMO_ENV', default='sandbox'),
    'PRIMARY_KEY': env('MTN_MOMO_PRIMARY_KEY', default=''),
    'API_USER': env('MTN_MOMO_API_USER', default=''),
    'API_KEY': env('MTN_MOMO_API_KEY', default=''),
    'TARGET_ENV': env('MTN_MOMO_TARGET_ENVIRONMENT', default='sandbox'),
    'CURRENCY': 'XAF',
}

# Cameroon SMS Gateway
SMS_GATEWAY = {
    'URL': env('SMS_GATEWAY_URL', default='https://api.sms-gateway-cameroon.local/v1/messages'),
    'API_KEY': env('SMS_GATEWAY_API_KEY', default=''),
    'SENDER_ID': env('SMS_SENDER_ID', default='HOSP_CMR'),
}

# Hospital profile
HOSPITAL_PROFILE = {
    'NAME': env('HOSPITAL_NAME', default='Centre Hospitalier Régional Universitaire'),
    'NAME_EN': env('HOSPITAL_NAME_EN', default='Regional University Teaching Hospital'),
    'PHONE': env('HOSPITAL_PHONE', default='+237 670 000 000'),
    'EMAIL': env('HOSPITAL_EMAIL', default='contact@hospital-cmr.local'),
    'ADDRESS': env('HOSPITAL_ADDRESS', default='Douala / Yaoundé, Cameroun'),
    'CURRENCY': 'FCFA',
}
