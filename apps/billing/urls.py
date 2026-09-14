from django.urls import path
from .views import (
    InvoiceListView, InvoiceDetailView, InvoiceAutoGenerateView,
    ProcessPaymentView, InvoiceReceiptPDFView, AccountingExportCSVView
)

app_name = 'billing'

urlpatterns = [
    path('invoices/', InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
    path('patient/<uuid:patient_id>/auto-generate/', InvoiceAutoGenerateView.as_view(), name='invoice_auto_generate'),
    path('invoices/<int:invoice_id>/pay/', ProcessPaymentView.as_view(), name='process_payment'),
    path('invoices/<int:pk>/receipt/pdf/', InvoiceReceiptPDFView.as_view(), name='receipt_pdf'),
    path('export/accounting/csv/', AccountingExportCSVView.as_view(), name='export_csv'),
]
