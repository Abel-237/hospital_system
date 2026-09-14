from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import LabTestType, LabOrder, LabOrderItem

class LabOrderItemInline(admin.TabularInline):
    model = LabOrderItem
    extra = 0

@admin.register(LabTestType)
class LabTestTypeAdmin(SimpleHistoryAdmin):
    list_display = ('code', 'name', 'category', 'price', 'unit', 'normal_range_min', 'normal_range_max', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('code', 'name')

@admin.register(LabOrder)
class LabOrderAdmin(SimpleHistoryAdmin):
    list_display = ('order_number', 'patient', 'prescribed_by', 'priority', 'status', 'created_at')
    list_filter = ('status', 'priority', 'created_at')
    search_fields = ('order_number', 'patient__matricule', 'patient__first_name', 'patient__last_name')
    inlines = [LabOrderItemInline]
