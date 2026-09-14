from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Invoice, InvoiceItem, Payment, InsurancePolicy

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    readonly_fields = ('payment_reference', 'status', 'operator_transaction_id')

@admin.register(InsurancePolicy)
class InsurancePolicyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'policy_number', 'patient', 'coverage_percentage', 'is_active')
    search_fields = ('company_name', 'policy_number', 'patient__matricule', 'patient__first_name', 'patient__last_name')

@admin.register(Invoice)
class InvoiceAdmin(SimpleHistoryAdmin):
    list_display = ('invoice_number', 'patient', 'total_gross', 'insurance_amount', 'patient_net_amount', 'paid_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('invoice_number', 'patient__matricule', 'patient__first_name', 'patient__last_name')
    inlines = [InvoiceItemInline, PaymentInline]

@admin.register(Payment)
class PaymentAdmin(SimpleHistoryAdmin):
    list_display = ('payment_reference', 'invoice', 'method', 'amount', 'status', 'received_by', 'created_at')
    list_filter = ('method', 'status', 'created_at')
    search_fields = ('payment_reference', 'operator_transaction_id', 'invoice__invoice_number')
