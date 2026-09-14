"""
Development settings for Hospital Management System.
"""
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# In dev, we can use local memory cache if Redis is not reachable, or Redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'hospital-dev-cache',
    }
}

# In local development, execute Celery tasks synchronously if broker is unreachable
CELERY_TASK_ALWAYS_EAGER = env.bool('CELERY_ALWAYS_EAGER', default=True)
CELERY_TASK_EAGER_PROPAGATES = True

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# CORS
CORS_ALLOW_ALL_ORIGINS = True

# Disable 2FA enforcement in development if needed for ease of testing
ENFORCE_2FA_IN_DEV = env.bool('ENFORCE_2FA_IN_DEV', default=False)
