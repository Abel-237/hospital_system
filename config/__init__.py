# config/__init__.py
"""Hospital Information System Configuration Package."""
from .celery import app as celery_app

__all__ = ('celery_app',)
