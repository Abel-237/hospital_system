# config/celery.py
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')

app = Celery('hospital_system')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Periodic Tasks Configuration
app.conf.beat_schedule = {
    # Send appointment reminders 24h & 2h before
    'send-appointment-reminders-hourly': {
        'task': 'apps.notifications.tasks.send_upcoming_appointment_reminders',
        'schedule': crontab(minute='0'),  # every hour
    },
    # Check pharmacy stock levels daily at 07:00
    'check-pharmacy-stock-daily': {
        'task': 'apps.notifications.tasks.check_critical_stock_and_notify',
        'schedule': crontab(hour='7', minute='0'),
    },
}
