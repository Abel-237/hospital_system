from django.urls import path
from .views import (
    MedicationListView, MedicationCreateView, StockBatchCreateView,
    PendingPrescriptionsView, DispensePrescriptionView
)

app_name = 'pharmacy'

urlpatterns = [
    path('', MedicationListView.as_view(), name='medication_list'),
    path('create/', MedicationCreateView.as_view(), name='medication_create'),
    path('batch/create/', StockBatchCreateView.as_view(), name='batch_create'),
    path('prescriptions/pending/', PendingPrescriptionsView.as_view(), name='pending_prescriptions'),
    path('prescriptions/<int:prescription_id>/dispense/', DispensePrescriptionView.as_view(), name='dispense_prescription'),
]
