import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from apps.core.models import TimeStampedModel
from apps.patients.models import Patient
from apps.consultations.models import Consultation

class LabTestType(TimeStampedModel):
    """
    Catalog of laboratory exams and imaging acts.
    """
    class Category(models.TextChoices):
        HEMATOLOGY = 'HEMATOLOGY', _('Hématologie')
        BIOCHEMISTRY = 'BIOCHEMISTRY', _('Biochimie')
        PARASITOLOGY = 'PARASITOLOGY', _('Parasitologie / Paludisme')
        MICROBIOLOGY = 'MICROBIOLOGY', _('Microbiologie / Bactériologie')
        SEROLOGY = 'SEROLOGY', _('Sérologie / Immunologie')
        IMAGING = 'IMAGING', _('Imagerie / Radiologie / Échographie')

    name = models.CharField(_('Nom de l’examen'), max_length=150)
    code = models.CharField(_('Code analyse'), max_length=30, unique=True)
    category = models.CharField(_('Catégorie'), max_length=30, choices=Category.choices, default=Category.HEMATOLOGY)
    price = models.DecimalField(_('Tarif conventionné (FCFA)'), max_digits=10, decimal_places=2)
    unit = models.CharField(_('Unité de mesure'), max_length=50, blank=True, help_text="Ex: g/dL, mg/L, /mm3")
    normal_range_min = models.CharField(_('Norme Min'), max_length=50, blank=True)
    normal_range_max = models.CharField(_('Norme Max'), max_length=50, blank=True)
    description = models.TextField(_('Conditions de prélèvement & Remarques'), blank=True)
    is_active = models.BooleanField(_('Disponible'), default=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Type d’examen de laboratoire')
        verbose_name_plural = _('Types d’examens de laboratoire')
        ordering = ['category', 'name']

    def __str__(self):
        return f"[{self.code}] {self.name}"


class LabOrder(TimeStampedModel):
    """
    Doctor request for laboratory examinations.
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('En attente de prélèvement')
        IN_PROGRESS = 'IN_PROGRESS', _('Analyses en cours')
        COMPLETED = 'COMPLETED', _('Résultats disponibles')
        CANCELLED = 'CANCELLED', _('Annulé')

    class Priority(models.TextChoices):
        NORMAL = 'NORMAL', _('Normal')
        URGENT = 'URGENT', _('Urgent')

    order_number = models.CharField(_('Numéro de bon'), max_length=50, unique=True)
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='lab_orders',
        verbose_name=_('Patient')
    )
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lab_orders',
        verbose_name=_('Consultation')
    )
    prescribed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='prescribed_lab_orders',
        limit_choices_to={'role': 'DOCTOR'},
        verbose_name=_('Médecin prescripteur')
    )
    status = models.CharField(_('Statut'), max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    priority = models.CharField(_('Priorité'), max_length=20, choices=Priority.choices, default=Priority.NORMAL)
    clinical_indications = models.TextField(_('Renseignements cliniques'), blank=True)
    completed_at = models.DateTimeField(_('Complété le'), null=True, blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Bon d’analyses laboratoire')
        verbose_name_plural = _('Bons d’analyses laboratoire')
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"LAB-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_number} - {self.patient.full_name} ({self.get_status_display()})"


class LabOrderItem(models.Model):
    order = models.ForeignKey(
        LabOrder,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Bon')
    )
    test_type = models.ForeignKey(
        LabTestType,
        on_delete=models.PROTECT,
        related_name='order_items',
        verbose_name=_('Examen')
    )
    result_value = models.CharField(_('Valeur mesurée / Constat'), max_length=255, blank=True)
    is_abnormal = models.BooleanField(_('Valeur anormale / Alerte'), default=False)
    technician_notes = models.TextField(_('Observations du biologiste'), blank=True)
    attachment = models.FileField(_('Cliché / Compte-rendu scanné'), upload_to='lab_results/', blank=True, null=True)
    analyzed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='analyzed_items',
        limit_choices_to={'role': 'LABORANT'},
        verbose_name=_('Laborantin / Biologiste')
    )
    analyzed_at = models.DateTimeField(_('Analysé le'), null=True, blank=True)

    class Meta:
        verbose_name = _('Résultat d’analyse')
        verbose_name_plural = _('Résultats d’analyses')

    def __str__(self):
        return f"{self.test_type.name}: {self.result_value or 'En attente'}"
