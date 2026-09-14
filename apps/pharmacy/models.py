from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from apps.core.models import TimeStampedModel
from apps.patients.models import Patient
from apps.consultations.models import Prescription

class Medication(TimeStampedModel):
    """
    Hospital formulary drug definition.
    """
    class Form(models.TextChoices):
        TABLET = 'TABLET', _('Comprimé / Gélule')
        SYRUP = 'SYRUP', _('Sirop / Suspension')
        INJECTABLE = 'INJECTABLE', _('Injectable / Perfusion')
        CREAM = 'CREAM', _('Pommade / Crème')
        DROPS = 'DROPS', _('Gouttes / Collyre')
        POWDER = 'POWDER', _('Poudre pour solution')

    name = models.CharField(_('Nom commercial'), max_length=150, db_index=True)
    dci = models.CharField(_('Dénomination Commune Internationale (DCI)'), max_length=150, db_index=True)
    form = models.CharField(_('Forme galénique'), max_length=20, choices=Form.choices, default=Form.TABLET)
    dosage = models.CharField(_('Dosage'), max_length=100, help_text="Ex: 500mg, 1g, 250mg/5ml")
    unit_price = models.DecimalField(_('Prix unitaire (FCFA)'), max_digits=10, decimal_places=2)
    critical_stock_threshold = models.PositiveIntegerField(
        _('Seuil d’alerte stock'),
        default=15,
        help_text=_("Déclenche une notification lorsque le stock disponible passe sous ce niveau")
    )
    description = models.TextField(_('Indications & Contre-indications'), blank=True)
    is_active = models.BooleanField(_('Actif au livret thérapeutique'), default=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Médicament')
        verbose_name_plural = _('Médicaments')
        ordering = ['name']

    def __str__(self):
        return f"{self.name} {self.dosage} ({self.get_form_display()})"

    @property
    def total_stock(self):
        return sum(b.quantity for b in self.batches.filter(expiration_date__gt=timezone.now().date()))

    @property
    def is_critical_stock(self):
        return self.total_stock <= self.critical_stock_threshold


class StockBatch(TimeStampedModel):
    """
    Physical lot/batch in pharmacy warehouse with expiration date.
    """
    medication = models.ForeignKey(
        Medication,
        on_delete=models.CASCADE,
        related_name='batches',
        verbose_name=_('Médicament')
    )
    batch_number = models.CharField(_('Numéro de Lot'), max_length=60)
    expiration_date = models.DateField(_('Date de péremption'), db_index=True)
    quantity = models.PositiveIntegerField(_('Quantité en stock'))
    purchase_price = models.DecimalField(_('Prix d’achat unitaire (FCFA)'), max_digits=10, decimal_places=2, default=0)
    received_date = models.DateField(_('Date de réception'), default=timezone.now)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Lot de Stock')
        verbose_name_plural = _('Lots de Stock')
        ordering = ['expiration_date']
        constraints = [
            models.UniqueConstraint(fields=['medication', 'batch_number'], name='unique_medication_batch')
        ]

    def __str__(self):
        return f"Lot {self.batch_number} - {self.medication.name} (Exp: {self.expiration_date})"

    @property
    def is_expired(self):
        return self.expiration_date <= timezone.now().date()

    @property
    def is_near_expiry(self):
        today = timezone.now().date()
        delta = (self.expiration_date - today).days
        return 0 < delta <= 60


class Dispensation(TimeStampedModel):
    """
    Delivery of medication to a patient against an electronic prescription.
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('En attente de délivrance')
        COMPLETED = 'COMPLETED', _('Délivrée')
        CANCELLED = 'CANCELLED', _('Annulée')

    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dispensations',
        verbose_name=_('Ordonnance')
    )
    patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT,
        related_name='dispensations',
        verbose_name=_('Patient')
    )
    dispensed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='dispensations',
        limit_choices_to={'role': 'PHARMACIST'},
        verbose_name=_('Pharmacien')
    )
    status = models.CharField(
        _('Statut'),
        max_length=20,
        choices=Status.choices,
        default=Status.COMPLETED
    )
    total_amount = models.DecimalField(_('Montant total (FCFA)'), max_digits=10, decimal_places=2, default=0)
    dispensed_at = models.DateTimeField(_('Délivrée le'), default=timezone.now)
    notes = models.TextField(_('Conseils de délivrance'), blank=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Délivrance de Médicaments')
        verbose_name_plural = _('Délivrances de Médicaments')
        ordering = ['-dispensed_at']

    def __str__(self):
        return f"Délivrance #{self.pk} - {self.patient.full_name} ({self.total_amount} FCFA)"


class DispensationItem(models.Model):
    dispensation = models.ForeignKey(
        Dispensation,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Délivrance')
    )
    medication = models.ForeignKey(
        Medication,
        on_delete=models.PROTECT,
        verbose_name=_('Médicament')
    )
    batch = models.ForeignKey(
        StockBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Lot prélevé')
    )
    quantity = models.PositiveIntegerField(_('Quantité délivrée'))
    unit_price = models.DecimalField(_('Prix unitaire (FCFA)'), max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(_('Sous-total (FCFA)'), max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.unit_price * self.quantity
        super().save(*args, **kwargs)
