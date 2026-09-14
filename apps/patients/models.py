import uuid
from datetime import date
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords
from apps.core.models import TimeStampedModel
from apps.core.utils import generate_matricule

class Patient(TimeStampedModel):
    """
    Electronic Health Record (Dossier Patient Informatisé).
    Independent business model; not a User account.
    Compliant with Cameroon Law n°2010/012.
    """
    class Gender(models.TextChoices):
        MALE = 'M', _('Masculin')
        FEMALE = 'F', _('Féminin')

    class BloodGroup(models.TextChoices):
        A_POS = 'A+', 'A+'
        A_NEG = 'A-', 'A-'
        B_POS = 'B+', 'B+'
        B_NEG = 'B-', 'B-'
        AB_POS = 'AB+', 'AB+'
        AB_NEG = 'AB-', 'AB-'
        O_POS = 'O+', 'O+'
        O_NEG = 'O-', 'O-'
        UNKNOWN = 'UNK', _('Inconnu')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    matricule = models.CharField(
        _('Matricule Patient'),
        max_length=30,
        unique=True,
        db_index=True,
        help_text=_("Identifiant unique hospitalier national/régional")
    )
    first_name = models.CharField(_('Prénom'), max_length=100)
    last_name = models.CharField(_('Nom de famille'), max_length=100)
    birth_date = models.DateField(_('Date de naissance'))
    gender = models.CharField(_('Sexe'), max_length=5, choices=Gender.choices)
    
    blood_group = models.CharField(
        _('Groupe Sanguin'),
        max_length=10,
        choices=BloodGroup.choices,
        default=BloodGroup.UNKNOWN
    )
    
    phone = models.CharField(_('Téléphone'), max_length=25)
    email = models.EmailField(_('Email'), blank=True)
    address = models.CharField(_('Adresse de résidence'), max_length=255, blank=True)
    city = models.CharField(_('Ville / Région'), max_length=100, default='Douala')
    
    # Emergency Contact
    emergency_contact_name = models.CharField(_('Contact d’urgence (Nom)'), max_length=100, blank=True)
    emergency_contact_phone = models.CharField(_('Contact d’urgence (Tél)'), max_length=25, blank=True)
    emergency_contact_relation = models.CharField(_('Lien de parenté'), max_length=50, blank=True)
    
    # Medical Background (Sensitive)
    allergies = models.TextField(_('Allergies connues'), blank=True, help_text=_("Médicaments, aliments, latex, etc."))
    chronic_conditions = models.TextField(_('Affections chroniques'), blank=True, help_text=_("HTA, Diabète, Drépanocytose, Asthme, etc."))
    family_history = models.TextField(_('Antécédents familiaux'), blank=True)
    surgical_history = models.TextField(_('Antécédents chirurgicaux'), blank=True)
    
    # Cameroon Data Privacy Law n°2010/012 Compliance
    consent_given = models.BooleanField(_('Consentement traitement données de santé'), default=True)
    consent_given_at = models.DateTimeField(_('Date/Heure du consentement'), null=True, blank=True)
    
    # Audit Trail
    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Dossier Patient')
        verbose_name_plural = _('Dossiers Patients')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.matricule} - {self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.matricule:
            self.matricule = generate_matricule(prefix="CMR")
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
