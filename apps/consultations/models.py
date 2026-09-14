import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from apps.core.models import TimeStampedModel
from apps.patients.models import Patient
from apps.appointments.models import Appointment

class VitalSigns(TimeStampedModel):
    """
    Vital signs recorded by nursing staff or physician.
    """
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='vital_signs_records',
        verbose_name=_('Patient')
    )
    recorded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='recorded_vitals',
        verbose_name=_('Enregistré par')
    )
    temperature = models.DecimalField(_('Température (°C)'), max_digits=4, decimal_places=1, help_text="Ex: 37.5")
    blood_pressure_systolic = models.PositiveIntegerField(_('Tension Systolique (mmHg)'), help_text="Ex: 120")
    blood_pressure_diastolic = models.PositiveIntegerField(_('Tension Diastolique (mmHg)'), help_text="Ex: 80")
    pulse_rate = models.PositiveIntegerField(_('Pouls (bpm)'), help_text="Ex: 75")
    respiratory_rate = models.PositiveIntegerField(_('Fréquence respiratoire (cpm)'), blank=True, null=True, help_text="Ex: 16")
    oxygen_saturation = models.DecimalField(_('Saturation O2 / SpO2 (%)'), max_digits=4, decimal_places=1, blank=True, null=True, help_text="Ex: 98.5")
    weight = models.DecimalField(_('Poids (kg)'), max_digits=5, decimal_places=2, blank=True, null=True, help_text="Ex: 72.5")
    height = models.DecimalField(_('Taille (cm)'), max_digits=5, decimal_places=1, blank=True, null=True, help_text="Ex: 175.0")
    notes = models.TextField(_('Remarques infirmières'), blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Constantes Vitales')
        verbose_name_plural = _('Constantes Vitales')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient.full_name} - {self.temperature}°C / {self.blood_pressure_systolic}/{self.blood_pressure_diastolic} mmHg"

    @property
    def bmi(self):
        if self.weight and self.height and self.height > 0:
            height_m = float(self.height) / 100.0
            return round(float(self.weight) / (height_m ** 2), 1)
        return None


class Consultation(TimeStampedModel):
    """
    Medical act performed by a Doctor.
    """
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultation',
        verbose_name=_('Rendez-vous associé')
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT,
        related_name='consultations',
        verbose_name=_('Patient')
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='conducted_consultations',
        limit_choices_to={'role': 'DOCTOR'},
        verbose_name=_('Médecin traitant')
    )
    vital_signs = models.ForeignKey(
        VitalSigns,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultations',
        verbose_name=_('Constantes associées')
    )
    symptoms = models.TextField(_('Plaintes & Symptômes'))
    physical_examination = models.TextField(_('Examen clinique'), blank=True)
    diagnosis = models.TextField(_('Diagnostic Médical / Hypothèse'))
    clinical_notes = models.TextField(_('Notes d’évolution & Conduite à tenir'), blank=True)
    is_confidential = models.BooleanField(_('Dossier hautement confidentiel'), default=False)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Consultation Médicale')
        verbose_name_plural = _('Consultations Médicales')
        ordering = ['-created_at']

    def __str__(self):
        return f"Consultation {self.patient.full_name} - Dr. {self.doctor.last_name} ({self.created_at.strftime('%d/%m/%Y')})"


class Prescription(TimeStampedModel):
    """
    Digital prescription associated with a consultation.
    """
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.CASCADE,
        related_name='prescriptions',
        verbose_name=_('Consultation')
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='prescriptions',
        verbose_name=_('Patient')
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='prescriptions',
        verbose_name=_('Médecin prescripteur')
    )
    code = models.CharField(_('Code Ordonnance'), max_length=50, unique=True)
    is_dispensed = models.BooleanField(_('Délivrée en pharmacie'), default=False)
    dispensed_at = models.DateTimeField(_('Date de délivrance'), null=True, blank=True)
    notes = models.TextField(_('Instructions générales'), blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Ordonnance Numérique')
        verbose_name_plural = _('Ordonnances Numériques')
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"RX-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.patient.full_name}"


class PrescriptionItem(models.Model):
    """
    Line item on an electronic prescription.
    """
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Ordonnance')
    )
    medication_name = models.CharField(_('Médicament (DCI / Nom commercial)'), max_length=200)
    dosage = models.CharField(_('Posologie'), max_length=150, help_text="Ex: 1 comprimé matin et soir")
    duration = models.CharField(_('Durée'), max_length=100, help_text="Ex: 7 jours")
    quantity = models.PositiveIntegerField(_('Quantité prescrite (boîtes/flacons)'), default=1)
    instructions = models.CharField(_('Précautions particulières'), max_length=255, blank=True, help_text="Ex: À prendre au milieu des repas")

    class Meta:
        verbose_name = _('Ligne d’ordonnance')
        verbose_name_plural = _('Lignes d’ordonnances')

    def __str__(self):
        return f"{self.medication_name} ({self.dosage})"
