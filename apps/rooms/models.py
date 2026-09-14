from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from apps.core.models import TimeStampedModel
from apps.patients.models import Patient

class Ward(TimeStampedModel):
    """
    Pavilion or hospital department division (e.g. Maternité, Médecine Interne, Pédiatrie).
    """
    name = models.CharField(_('Nom du Pavillon / Service'), max_length=100)
    code = models.CharField(_('Code'), max_length=20, unique=True)
    floor = models.CharField(_('Étage / Emplacement'), max_length=50, blank=True)
    description = models.TextField(_('Description'), blank=True)

    class Meta:
        verbose_name = _('Pavillon Hospitalier')
        verbose_name_plural = _('Pavillons Hospitaliers')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class Room(TimeStampedModel):
    """
    Hospital room inside a ward.
    """
    class RoomType(models.TextChoices):
        STANDARD = 'STANDARD', _('Chambre Commune / Standard')
        VIP = 'VIP', _('Chambre Individuelle VIP')
        INTENSIVE_CARE = 'ICU', _('Soins Intensifs / Réanimation')
        ISOLATION = 'ISOLATION', _('Isolement Infectieux')

    ward = models.ForeignKey(
        Ward,
        on_delete=models.CASCADE,
        related_name='rooms',
        verbose_name=_('Pavillon')
    )
    room_number = models.CharField(_('Numéro de chambre'), max_length=30)
    room_type = models.CharField(_('Type'), max_length=20, choices=RoomType.choices, default=RoomType.STANDARD)
    daily_rate = models.DecimalField(_('Tarif journalier (FCFA)'), max_digits=10, decimal_places=2, default=10000)

    class Meta:
        verbose_name = _('Chambre')
        verbose_name_plural = _('Chambres')
        ordering = ['ward', 'room_number']
        constraints = [
            models.UniqueConstraint(fields=['ward', 'room_number'], name='unique_room_in_ward')
        ]

    def __str__(self):
        return f"{self.ward.code} - Ch. {self.room_number} ({self.get_room_type_display()})"


class Bed(TimeStampedModel):
    """
    Individual hospital bed.
    """
    class Status(models.TextChoices):
        AVAILABLE = 'AVAILABLE', _('Disponible')
        OCCUPIED = 'OCCUPIED', _('Occupé')
        MAINTENANCE = 'MAINTENANCE', _('En maintenance / Nettoyage')
        RESERVED = 'RESERVED', _('Réservé')

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='beds',
        verbose_name=_('Chambre')
    )
    bed_number = models.CharField(_('Numéro de lit'), max_length=20)
    status = models.CharField(_('Statut'), max_length=20, choices=Status.choices, default=Status.AVAILABLE, db_index=True)

    class Meta:
        verbose_name = _('Lit d’hospitalisation')
        verbose_name_plural = _('Lits d’hospitalisation')
        ordering = ['room', 'bed_number']
        constraints = [
            models.UniqueConstraint(fields=['room', 'bed_number'], name='unique_bed_in_room')
        ]

    def __str__(self):
        return f"{self.room.ward.code} - Ch.{self.room.room_number} Lit {self.bed_number}"


class Admission(TimeStampedModel):
    """
    Inpatient hospital stay record.
    """
    patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT,
        related_name='admissions',
        verbose_name=_('Patient')
    )
    bed = models.ForeignKey(
        Bed,
        on_delete=models.PROTECT,
        related_name='admissions',
        verbose_name=_('Lit attribué')
    )
    admitting_doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='admissions',
        limit_choices_to={'role': 'DOCTOR'},
        verbose_name=_('Médecin prescripteur')
    )
    admission_date = models.DateTimeField(_('Date d’admission'), default=timezone.now)
    discharge_date = models.DateTimeField(_('Date de sortie'), null=True, blank=True)
    admission_reason = models.TextField(_('Motif d’hospitalisation'))
    discharge_summary = models.TextField(_('Résumé de sortie (Épicrise)'), blank=True)
    discharge_authorized_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='authorized_discharges',
        verbose_name=_('Sortie autorisée par')
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Séjour Hospitalier (Admission)')
        verbose_name_plural = _('Séjours Hospitaliers (Admissions)')
        ordering = ['-admission_date']

    def __str__(self):
        status_str = _("Actif") if not self.discharge_date else _("Sorti")
        return f"Admission {self.patient.full_name} ({self.bed}) - {status_str}"

    @property
    def is_active(self):
        return self.discharge_date is None

    @property
    def duration_days(self):
        end_time = self.discharge_date or timezone.now()
        days = (end_time.date() - self.admission_date.date()).days
        return max(1, days)


class NursingNote(TimeStampedModel):
    """
    Daily nursing care notes and observations.
    """
    admission = models.ForeignKey(
        Admission,
        on_delete=models.CASCADE,
        related_name='nursing_notes',
        verbose_name=_('Séjour')
    )
    nurse = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='nursing_notes',
        limit_choices_to={'role': 'NURSE'},
        verbose_name=_('Infirmier(ère)')
    )
    note_time = models.DateTimeField(_('Heure du soin / tour'), default=timezone.now)
    observation = models.TextField(_('Observations cliniques'))
    administered_treatments = models.TextField(_('Soins et traitements administrés'), blank=True)

    class Meta:
        verbose_name = _('Transmission Infirmière')
        verbose_name_plural = _('Transmissions Infirmières')
        ordering = ['-note_time']

    def __str__(self):
        return f"{self.admission.patient.full_name} - {self.note_time.strftime('%d/%m %H:%M')}"
