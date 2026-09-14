from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(SimpleHistoryAdmin):
    list_display = ('scheduled_date', 'scheduled_time', 'patient', 'doctor', 'priority', 'status', 'queue_number')
    list_filter = ('status', 'priority', 'scheduled_date', 'doctor')
    search_fields = ('patient__matricule', 'patient__first_name', 'patient__last_name', 'doctor__last_name', 'reason')
    ordering = ('-scheduled_date', 'scheduled_time')
