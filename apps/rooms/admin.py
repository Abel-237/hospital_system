from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Ward, Room, Bed, Admission, NursingNote

class BedInline(admin.TabularInline):
    model = Bed
    extra = 2

class RoomInline(admin.TabularInline):
    model = Room
    extra = 1

@admin.register(Ward)
class WardAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'floor')
    inlines = [RoomInline]

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('ward', 'room_number', 'room_type', 'daily_rate')
    list_filter = ('ward', 'room_type')
    inlines = [BedInline]

@admin.register(Bed)
class BedAdmin(admin.ModelAdmin):
    list_display = ('bed_number', 'room', 'status')
    list_filter = ('status', 'room__ward')

@admin.register(Admission)
class AdmissionAdmin(SimpleHistoryAdmin):
    list_display = ('patient', 'bed', 'admitting_doctor', 'admission_date', 'discharge_date')
    list_filter = ('admission_date', 'discharge_date')
    search_fields = ('patient__matricule', 'patient__first_name', 'patient__last_name')

@admin.register(NursingNote)
class NursingNoteAdmin(admin.ModelAdmin):
    list_display = ('admission', 'nurse', 'note_time')
