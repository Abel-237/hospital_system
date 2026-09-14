from django.urls import path
from .views import (
    ConsultationListView, VitalSignsCreateView, ConsultationCreateView,
    ConsultationDetailView, PrescriptionCreateView, PrescriptionPDFView
)

app_name = 'consultations'

urlpatterns = [
    path('', ConsultationListView.as_view(), name='consultation_list'),
    path('vitals/create/', VitalSignsCreateView.as_view(), name='vitals_create'),
    path('patient/<uuid:patient_id>/create/', ConsultationCreateView.as_view(), name='consultation_create'),
    path('<int:pk>/', ConsultationDetailView.as_view(), name='consultation_detail'),
    path('<int:consultation_id>/prescription/create/', PrescriptionCreateView.as_view(), name='prescription_create'),
    path('prescription/<int:pk>/pdf/', PrescriptionPDFView.as_view(), name='prescription_pdf'),
]
