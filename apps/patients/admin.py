from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(SimpleHistoryAdmin):
    list_display = ('matricule', 'first_name', 'last_name', 'gender', 'birth_date', 'blood_group', 'phone', 'city', 'consent_given')
    list_filter = ('gender', 'blood_group', 'consent_given', 'city')
    search_fields = ('matricule', 'first_name', 'last_name', 'phone', 'emergency_contact_name')
    readonly_fields = ('matricule', 'created_at', 'updated_at', 'consent_given_at')
