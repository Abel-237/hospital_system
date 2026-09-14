from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.core.models import TimeStampedModel

class NotificationLog(TimeStampedModel):
    class Channel(models.TextChoices):
        SMS = 'SMS', _('SMS Mobile (Cameroun)')
        EMAIL = 'EMAIL', _('Email')

    class Status(models.TextChoices):
        PENDING = 'PENDING', _('En attente')
        SENT = 'SENT', _('Envoyé avec succès')
        FAILED = 'FAILED', _('Échec d’envoi')

    recipient = models.CharField(_('Destinataire (Tél ou Email)'), max_length=150, db_index=True)
    channel = models.CharField(_('Canal'), max_length=10, choices=Channel.choices, default=Channel.SMS)
    subject = models.CharField(_('Objet / Titre'), max_length=200, blank=True)
    message = models.TextField(_('Contenu du message'))
    status = models.CharField(_('Statut'), max_length=15, choices=Status.choices, default=Status.PENDING, db_index=True)
    error_message = models.TextField(_('Message d’erreur'), blank=True)
    sent_at = models.DateTimeField(_('Envoyé le'), null=True, blank=True)

    class Meta:
        verbose_name = _('Journal de notification')
        verbose_name_plural = _('Journaux de notifications')
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.channel}] {self.recipient} - {self.get_status_display()}"
