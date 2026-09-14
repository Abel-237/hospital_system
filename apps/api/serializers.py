from rest_framework import serializers
from apps.patients.models import Patient
from apps.appointments.models import Appointment
from apps.consultations.models import Consultation, VitalSigns, Prescription, PrescriptionItem
from apps.pharmacy.models import Medication
from apps.rooms.models import Bed
from apps.billing.models import Invoice, Payment

class PatientSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Patient
        fields = [
            'id', 'matricule', 'first_name', 'last_name', 'full_name', 'age',
            'birth_date', 'gender', 'blood_group', 'phone', 'email', 'city',
            'emergency_contact_name', 'emergency_contact_phone',
            'allergies', 'chronic_conditions', 'consent_given', 'consent_given_at',
            'created_at'
        ]
        read_only_fields = ['id', 'matricule', 'created_at']


class VitalSignsSerializer(serializers.ModelSerializer):
    bmi = serializers.ReadOnlyField()
    recorded_by_name = serializers.ReadOnlyField(source='recorded_by.full_name')

    class Meta:
        model = VitalSigns
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.ReadOnlyField(source='patient.full_name')
    patient_matricule = serializers.ReadOnlyField(source='patient.matricule')
    doctor_name = serializers.ReadOnlyField(source='doctor.display_title')

    class Meta:
        model = Appointment
        fields = '__all__'


class PrescriptionItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrescriptionItem
        fields = '__all__'


class PrescriptionSerializer(serializers.ModelSerializer):
    items = PrescriptionItemSerializer(many=True, read_only=True)

    class Meta:
        model = Prescription
        fields = '__all__'


class ConsultationSerializer(serializers.ModelSerializer):
    vital_signs_detail = VitalSignsSerializer(source='vital_signs', read_only=True)
    prescriptions = PrescriptionSerializer(many=True, read_only=True)
    patient_name = serializers.ReadOnlyField(source='patient.full_name')
    doctor_name = serializers.ReadOnlyField(source='doctor.display_title')

    class Meta:
        model = Consultation
        fields = '__all__'


class MedicationSerializer(serializers.ModelSerializer):
    total_stock = serializers.ReadOnlyField()
    is_critical_stock = serializers.ReadOnlyField()

    class Meta:
        model = Medication
        fields = '__all__'


class BedSerializer(serializers.ModelSerializer):
    room_number = serializers.ReadOnlyField(source='room.room_number')
    ward_name = serializers.ReadOnlyField(source='room.ward.name')

    class Meta:
        model = Bed
        fields = '__all__'


class InvoiceSerializer(serializers.ModelSerializer):
    patient_name = serializers.ReadOnlyField(source='patient.full_name')
    remaining_balance = serializers.ReadOnlyField()

    class Meta:
        model = Invoice
        fields = '__all__'
