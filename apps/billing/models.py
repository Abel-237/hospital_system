import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from apps.core.models import TimeStampedModel
from apps.patients.models import Patient
from apps.consultations.models import Consultation
from apps.rooms.models import Admission

class InsurancePolicy(TimeStampedModel):
    """
    Patient health insurance or mutual fund coverage (Tiers-Payant).
    """
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name='insurance_policies',
        verbose_name=_('Assuré')
    )
    company_name = models.CharField(_('Compagnie d’assurance / Mutuelle'), max_length=120)
    policy_number = models.CharField(_('Numéro d’assuré / Police'), max_length=60)
    coverage_percentage = models.DecimalField(
        _('Taux de couverture (%)'),
        max_digits=5,
        decimal_places=2,
        default=Decimal('80.00'),
        help_text="Ex: 80% (le patient ne paie que le ticket modérateur de 20%)"
    )
    valid_until = models.DateField(_('Date d’expiration de la police'), null=True, blank=True)
    is_active = models.BooleanField(_('Police active'), default=True)

    class Meta:
        verbose_name = _('Police d’Assurance / Mutuelle')
        verbose_name_plural = _('Polices d’Assurance / Mutuelles')

    def __str__(self):
        return f"{self.company_name} - {self.policy_number} ({self.coverage_percentage}%)"


class Invoice(TimeStampedModel):
    """
    Consolidated medical bill.
    """
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Brouillon')
        PENDING = 'PENDING', _('En attente de paiement')
        PARTIALLY_PAID = 'PARTIALLY_PAID', _('Partiellement réglée')
        PAID = 'PAID', _('Réglée / Soldée')
        CANCELLED = 'CANCELLED', _('Annulée')

    invoice_number = models.CharField(_('Numéro de facture'), max_length=50, unique=True, db_index=True)
    patient = models.ForeignKey(
        Patient,
        on_delete=models.PROTECT,
        related_name='invoices',
        verbose_name=_('Patient')
    )
    consultation = models.ForeignKey(
        Consultation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        verbose_name=_('Consultation liée')
    )
    admission = models.ForeignKey(
        Admission,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        verbose_name=_('Séjour lié')
    )
    insurance_policy = models.ForeignKey(
        InsurancePolicy,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        verbose_name=_('Prise en charge assurance')
    )
    status = models.CharField(_('Statut'), max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    total_gross = models.DecimalField(_('Montant Brut Total (FCFA)'), max_digits=12, decimal_places=2, default=0)
    insurance_amount = models.DecimalField(_('Part Prise en Charge Assurance (FCFA)'), max_digits=12, decimal_places=2, default=0)
    patient_net_amount = models.DecimalField(_('Net à Payer Patient / Ticket Modérateur (FCFA)'), max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(_('Montant déjà encaissé (FCFA)'), max_digits=12, decimal_places=2, default=0)
    due_date = models.DateField(_('Date d’échéance'), default=timezone.now)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Facture')
        verbose_name_plural = _('Factures')
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            self.invoice_number = f"FAC-{timezone.now().year}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invoice_number} - {self.patient.full_name} ({self.patient_net_amount} FCFA)"

    @property
    def remaining_balance(self):
        return max(Decimal('0.00'), self.patient_net_amount - self.paid_amount)

    def recalculate_totals(self):
        gross = sum((item.subtotal for item in self.items.all()), Decimal('0.00'))
        self.total_gross = gross
        if self.insurance_policy and self.insurance_policy.is_active:
            rate = self.insurance_policy.coverage_percentage / Decimal('100.00')
            self.insurance_amount = round(gross * rate, 2)
            self.patient_net_amount = round(gross - self.insurance_amount, 2)
        else:
            self.insurance_amount = Decimal('0.00')
            self.patient_net_amount = gross

        if self.paid_amount >= self.patient_net_amount and self.patient_net_amount > 0:
            self.status = self.Status.PAID
        elif self.paid_amount > 0:
            self.status = self.Status.PARTIALLY_PAID
        self.save()


class InvoiceItem(models.Model):
    class Category(models.TextChoices):
        CONSULTATION = 'CONSULTATION', _('Consultation Médicale')
        PHARMACY = 'PHARMACY', _('Pharmacie & Médicaments')
        LABORATORY = 'LABORATORY', _('Examens de Laboratoire & Imagerie')
        HOSPITALIZATION = 'HOSPITALIZATION', _('Chambre & Hospitalisation')
        ACT = 'ACT', _('Acte Spécialisé / Chirurgie')

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name=_('Facture')
    )
    description = models.CharField(_('Désignation de la prestation'), max_length=255)
    category = models.CharField(_('Catégorie'), max_length=20, choices=Category.choices, default=Category.ACT)
    quantity = models.PositiveIntegerField(_('Quantité'), default=1)
    unit_price = models.DecimalField(_('Prix unitaire (FCFA)'), max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(_('Sous-total (FCFA)'), max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = Decimal(str(self.unit_price)) * self.quantity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.description} x{self.quantity} = {self.subtotal} FCFA"


class Payment(TimeStampedModel):
    """
    Transaction log supporting Cash, Card, Orange Money, and MTN Mobile Money.
    """
    class Method(models.TextChoices):
        CASH = 'CASH', _('Espèces / Caisse')
        BANK_CARD = 'CARD', _('Carte Bancaire (TPE)')
        ORANGE_MONEY = 'ORANGE_MONEY', _('Orange Money Cameroun')
        MTN_MOMO = 'MTN_MOMO', _('MTN Mobile Money Cameroun')
        INSURANCE_CHECK = 'INSURANCE', _('Chèque / Virement Assureur')

    class Status(models.TextChoices):
        INITIATED = 'INITIATED', _('Paiement initié')
        PENDING_USSD = 'PENDING_USSD', _('Invite USSD envoyée au client')
        SUCCESS = 'SUCCESS', _('Succès / Encaissé')
        FAILED = 'FAILED', _('Échec de la transaction')
        CANCELLED = 'CANCELLED', _('Annulé par l’utilisateur')

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.PROTECT,
        related_name='payments',
        verbose_name=_('Facture')
    )
    payment_reference = models.CharField(_('Référence paiement'), max_length=60, unique=True, db_index=True)
    method = models.CharField(_('Mode de règlement'), max_length=20, choices=Method.choices)
    amount = models.DecimalField(_('Montant versé (FCFA)'), max_digits=12, decimal_places=2)
    payer_phone = models.CharField(_('Numéro de téléphone payeur'), max_length=25, blank=True, help_text="Format: +237 6XX XX XX XX pour Mobile Money")
    status = models.CharField(_('Statut du paiement'), max_length=20, choices=Status.choices, default=Status.INITIATED, db_index=True)
    
    operator_transaction_id = models.CharField(_('ID Transaction Opérateur (Orange/MTN)'), max_length=100, blank=True)
    gateway_payload = models.JSONField(_('Détails réponse API passerelle'), default=dict, blank=True)
    
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='processed_payments',
        limit_choices_to={'role': 'CASHIER'},
        verbose_name=_('Caissier')
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Paiement / Encaissement')
        verbose_name_plural = _('Paiements / Encaissements')
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.payment_reference:
            self.payment_reference = f"PAY-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.payment_reference} - {self.amount} FCFA ({self.get_method_display()} - {self.get_status_display()})"
