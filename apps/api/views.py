from rest_framework import viewsets, permissions, filters
from apps.core.permissions import HasRolePermission
from apps.patients.models import Patient
from apps.appointments.models import Appointment
from apps.consultations.models import Consultation
from apps.pharmacy.models import Medication
from apps.rooms.models import Bed
from apps.billing.models import Invoice
from .serializers import (
    PatientSerializer, AppointmentSerializer, ConsultationSerializer,
    MedicationSerializer, BedSerializer, InvoiceSerializer
)

class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['matricule', 'first_name', 'last_name', 'phone']
    ordering_fields = ['created_at', 'last_name']


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.select_related('patient', 'doctor').all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['patient__matricule', 'patient__last_name', 'doctor__last_name']
    ordering_fields = ['scheduled_date', 'scheduled_time', 'priority']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == 'DOCTOR':
            return qs.filter(doctor=self.request.user)
        return qs


class ConsultationViewSet(viewsets.ModelViewSet):
    queryset = Consultation.objects.select_related('patient', 'doctor', 'vital_signs').prefetch_related('prescriptions__items').all()
    serializer_class = ConsultationSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    allowed_roles = ['DOCTOR', 'ADMIN', 'NURSE']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.role == 'DOCTOR':
            return qs.filter(doctor=self.request.user)
        return qs


class MedicationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Medication.objects.prefetch_related('batches').filter(is_active=True)
    serializer_class = MedicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'dci']


class BedViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Bed.objects.select_related('room__ward').all()
    serializer_class = BedSerializer
    permission_classes = [permissions.IsAuthenticated]


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.select_related('patient').prefetch_related('items', 'payments').all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated, HasRolePermission]
    allowed_roles = ['CASHIER', 'ADMIN']
