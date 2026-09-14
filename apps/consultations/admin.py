from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import VitalSigns, Consultation, Prescription, PrescriptionItem

class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1

@admin.register(VitalSigns)
class VitalSignsAdmin(SimpleHistoryAdmin):
    list_display = ('patient', 'temperature', 'blood_pressure_systolic', 'blood_pressure_diastolic', 'pulse_rate', 'recorded_by', 'created_at')
    search_fields = ('patient__matricule', 'patient__first_name', 'patient__last_name')

@admin.register(Consultation)
class ConsultationAdmin(SimpleHistoryAdmin):
    list_display = ('patient', 'doctor', 'diagnosis', 'created_at', 'is_confidential')
    search_fields = ('patient__matricule', 'patient__first_name', 'patient__last_name', 'diagnosis')
    list_filter = ('doctor', 'created_at', 'is_confidential')

@admin.register(Prescription)
class PrescriptionAdmin(SimpleHistoryAdmin):
    list_display = ('code', 'patient', 'doctor', 'is_dispensed', 'created_at')
    list_filter = ('is_dispensed', 'created_at')
    search_fields = ('code', 'patient__matricule', 'patient__first_name', 'patient__last_name')
    inlines = [PrescriptionItemInline]
