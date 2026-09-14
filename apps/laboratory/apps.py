from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class LaboratoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.laboratory'
    verbose_name = _('Laboratoire d’Analyses & Imagerie')
