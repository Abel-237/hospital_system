from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Medication, StockBatch, Dispensation, DispensationItem

class StockBatchInline(admin.TabularInline):
    model = StockBatch
    extra = 1

class DispensationItemInline(admin.TabularInline):
    model = DispensationItem
    extra = 0
    readonly_fields = ('subtotal',)

@admin.register(Medication)
class MedicationAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'dci', 'form', 'dosage', 'unit_price', 'total_stock', 'is_critical_stock', 'is_active')
    list_filter = ('form', 'is_active')
    search_fields = ('name', 'dci')
    inlines = [StockBatchInline]

@admin.register(StockBatch)
class StockBatchAdmin(SimpleHistoryAdmin):
    list_display = ('batch_number', 'medication', 'expiration_date', 'quantity', 'is_expired', 'is_near_expiry')
    list_filter = ('expiration_date',)
    search_fields = ('batch_number', 'medication__name')

@admin.register(Dispensation)
class DispensationAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'patient', 'dispensed_by', 'total_amount', 'status', 'dispensed_at')
    list_filter = ('status', 'dispensed_at')
    inlines = [DispensationItemInline]
