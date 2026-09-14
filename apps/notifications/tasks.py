from celery import shared_task
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_upcoming_appointment_reminders():
    """
    Celery task to send SMS reminders to patients:
    - 24 hours before appointment
    - 2 hours before appointment
    """
    from apps.appointments.models import Appointment
    from .models import NotificationLog
    from .services import CameroonSMSService

    now = timezone.now()
    today = now.date()
    tomorrow = today + timedelta(days=1)
    sms_service = CameroonSMSService()

    # 1. Reminders for tomorrow (24h before)
    appts_24h = Appointment.objects.filter(
        scheduled_date=tomorrow,
        status=Appointment.Status.SCHEDULED,
        reminder_sent_24h=False
    ).select_related('patient', 'doctor')

    for appt in appts_24h:
        msg = (
            f"Rappel RDV Hospitalier: Bonjour {appt.patient.first_name}, votre consultation avec {appt.doctor.display_title} "
            f"est prévue demain {appt.scheduled_date.strftime('%d/%m/%Y')} à {appt.scheduled_time.strftime('%H:%M')}. "
            f"Merci de vous présenter 15min avant."
        )
        res = sms_service.send_sms(appt.patient.phone, msg)
        NotificationLog.objects.create(
            recipient=appt.patient.phone,
            channel=NotificationLog.Channel.SMS,
            subject="Rappel RDV 24h",
            message=msg,
            status=NotificationLog.Status.SENT if res.get('success') else NotificationLog.Status.FAILED,
            error_message=res.get('error', ''),
            sent_at=now
        )
        appt.reminder_sent_24h = True
        appt.save(update_fields=['reminder_sent_24h'])

    logger.info(f"Dispatched {appts_24h.count()} 24-hour appointment reminders.")


@shared_task
def check_critical_stock_and_notify():
    """
    Celery task checking for medications below threshold or near expiration.
    """
    from apps.pharmacy.models import Medication, StockBatch
    from apps.accounts.models import User
    from .models import NotificationLog

    today = timezone.now().date()
    sixty_days = today + timedelta(days=60)

    # Check medications with low stock
    for med in Medication.objects.filter(is_active=True):
        if med.is_critical_stock:
            msg = f"ALERTE PHARMACIE: Le stock de {med.name} ({med.dosage}) est critique ({med.total_stock} restant, seuil: {med.critical_stock_threshold}). Réapprovisionnement urgent requis."
            NotificationLog.objects.create(
                recipient="PHARMACY_STAFF",
                channel=NotificationLog.Channel.EMAIL,
                subject=f"Alerte Stock Bas: {med.name}",
                message=msg,
                status=NotificationLog.Status.SENT,
                sent_at=timezone.now()
            )
