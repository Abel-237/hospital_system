from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from apps.core.models import TimeStampedModel
from apps.patients.models import Patient

class Appointment(TimeStampedModel):
    """
    Doctor appointment and waiting room queue ticket.
    """
    class Status(models.TextChoices):
        SCHEDULED = 'SCHEDULED', _('Planifié')
        WAITING = 'WAITING', _('En salle d’attente')
        IN_CONSULTATION = 'IN_CONSULTATION', _('En consultation')
        COMPLETED = 'COMPLETED', _('Terminé')
        CANCELLED = 'CANCELLED', _('Annulé')
        NO_SHOW = 'NO_SHOW', _('Absent')

    class Priority(models.TextChoices):
        NORMAL = 'NORMAL', _('Normal')
        URGENT = 'URGENT', _('Urgent')
        EMERGENCY = 'EMERGENCY', _('Urgence Vitale')

    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='appointments',
        verbose_name=_('Patient')
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='doctor_appointments',
        limit_choices_to={'role': 'DOCTOR'},
        verbose_name=_('Médecin')
    )
    scheduled_date = models.DateField(_('Date prévue'), db_index=True)
    scheduled_time = models.TimeField(_('Heure prévue'))
    estimated_duration = models.PositiveIntegerField(_('Durée estimée (minutes)'), default=30)
    
    reason = models.CharField(_('Motif du rendez-vous'), max_length=255)
    priority = models.CharField(
        _('Priorité'),
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL
    )
    status = models.CharField(
        _('Statut'),
        max_length=20,
        choices=Status.choices,
        default=Status.SCHEDULED,
        db_index=True
    )
    
    queue_number = models.PositiveIntegerField(_('Numéro de file'), blank=True, null=True)
    arrival_time = models.DateTimeField(_('Heure d’arrivée'), blank=True, null=True)
    
    # Automated reminders tracking
    reminder_sent_24h = models.BooleanField(_('Rappel 24h envoyé'), default=False)
    reminder_sent_2h = models.BooleanField(_('Rappel 2h envoyé'), default=False)
    
    notes = models.TextField(_('Notes internes'), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_appointments',
        verbose_name=_('Créé par')
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Rendez-vous')
        verbose_name_plural = _('Rendez-vous')
        ordering = ['scheduled_date', 'scheduled_time']
        # Prevent exact duplicate booking for the same doctor at the same slot
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'scheduled_date', 'scheduled_time'],
                name='unique_doctor_slot'
            )
        ]

    def __str__(self):
        return f"{self.scheduled_date} {self.scheduled_time} - {self.patient.full_name} ({self.doctor.display_title})"
