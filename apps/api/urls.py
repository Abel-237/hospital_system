from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PatientViewSet, AppointmentViewSet, ConsultationViewSet,
    MedicationViewSet, BedViewSet, InvoiceViewSet
)

router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='api_patient')
router.register(r'appointments', AppointmentViewSet, basename='api_appointment')
router.register(r'consultations', ConsultationViewSet, basename='api_consultation')
router.register(r'medications', MedicationViewSet, basename='api_medication')
router.register(r'beds', BedViewSet, basename='api_bed')
router.register(r'invoices', InvoiceViewSet, basename='api_invoice')

app_name = 'api'

urlpatterns = [
    path('', include(router.urls)),
]
