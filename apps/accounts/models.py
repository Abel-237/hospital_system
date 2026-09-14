from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

class User(AbstractUser):
    """
    Hospital staff user model.
    Patients are NOT users of this system (separate Patient model).
    """
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrateur')
        DOCTOR = 'DOCTOR', _('Médecin')
        NURSE = 'NURSE', _('Infirmier')
        RECEPTIONIST = 'RECEPTIONIST', _('Réceptionniste')
        PHARMACIST = 'PHARMACIST', _('Pharmacien')
        LABORANT = 'LABORANT', _('Laborantin')
        CASHIER = 'CASHIER', _('Caissier')

    role = models.CharField(
        _('Rôle'),
        max_length=20,
        choices=Role.choices,
        default=Role.RECEPTIONIST,
        help_text=_("Définit les permissions et la vue d'accueil du personnel")
    )
    phone_number = models.CharField(
        _('Téléphone'),
        max_length=20,
        blank=True,
        help_text=_("Format camerounais: +237 6XX XX XX XX")
    )
    speciality = models.CharField(
        _('Spécialité / Service'),
        max_length=100,
        blank=True,
        help_text=_("Ex: Cardiologie, Pédiatrie, Urgences")
    )
    license_number = models.CharField(
        _("Numéro d'Ordre"),
        max_length=50,
        blank=True,
        help_text=_("Numéro d'inscription à l'Ordre National des Médecins ou Pharmaciens")
    )
    is_2fa_enabled = models.BooleanField(
        _('2FA Activé'),
        default=False,
        help_text=_("Obligatoire pour les rôles Médecin, Pharmacien, Administrateur")
    )
    avatar = models.ImageField(
        _('Photo de profil'),
        upload_to='avatars/%Y/%m/',
        blank=True,
        null=True,
        help_text=_("Format PNG, JPG ou WebP (max. 2 Mo)")
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = _('Personnel de santé')
        verbose_name_plural = _('Personnel de santé')
        ordering = ['last_name', 'first_name']

    @property
    def full_name(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name if name else self.username

    @property
    def initials(self):
        first = self.first_name[0] if self.first_name else (self.username[0] if self.username else '')
        last = self.last_name[0] if self.last_name else ''
        res = f"{first}{last}".upper()
        return res if res else "U"

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            try:
                return self.avatar.url
            except Exception:
                return None
        return None

    @property
    def display_title(self):
        if self.role == self.Role.DOCTOR:
            return f"Dr. {self.full_name}"
        return self.full_name

    def is_2fa_mandatory(self):
        """Check if 2FA is strictly mandated for this role."""
        return self.role in [self.Role.ADMIN, self.Role.DOCTOR, self.Role.PHARMACIST] or self.is_superuser
