"""
Tests for the consultations application:
- VitalSigns model & BMI calculation
- Consultation creation
- Prescription and PrescriptionItem
- ConsultationListView (role-based filtering)
- PrescriptionPDFView fallback to HTML
"""
import pytest
from datetime import date
from decimal import Decimal
from django.urls import reverse
from django.utils import timezone
from apps.consultations.models import Consultation, VitalSigns, Prescription, PrescriptionItem
from apps.appointments.models import Appointment


@pytest.mark.django_db
class TestVitalSignsModel:
    def test_bmi_calculation(self, patient, doctor_user):
        vs = VitalSigns.objects.create(
            patient=patient,
            recorded_by=doctor_user,
            temperature=Decimal('37.2'),
            blood_pressure_systolic=120,
            blood_pressure_diastolic=80,
            pulse_rate=72,
            weight=Decimal('70.0'),
            height=Decimal('175.0'),
        )
        assert vs.bmi == round(70.0 / (1.75 ** 2), 1)

    def test_bmi_none_when_height_missing(self, patient, doctor_user):
        vs = VitalSigns.objects.create(
            patient=patient,
            recorded_by=doctor_user,
            temperature=Decimal('36.8'),
            blood_pressure_systolic=110,
            blood_pressure_diastolic=70,
            pulse_rate=68,
        )
        assert vs.bmi is None

    def test_str_representation(self, patient, doctor_user):
        vs = VitalSigns.objects.create(
            patient=patient,
            recorded_by=doctor_user,
            temperature=Decimal('38.0'),
            blood_pressure_systolic=130,
            blood_pressure_diastolic=85,
            pulse_rate=80,
        )
        assert patient.full_name in str(vs)
        assert "38.0°C" in str(vs)


@pytest.mark.django_db
class TestConsultationModel:
    def test_consultation_creation(self, patient, doctor_user):
        c = Consultation.objects.create(
            patient=patient,
            doctor=doctor_user,
            symptoms="Fièvre et céphalées depuis 3 jours.",
            diagnosis="Paludisme simple",
        )
        assert c.pk is not None
        assert c.patient == patient
        assert c.doctor == doctor_user
        assert str(patient.full_name) in str(c)

    def test_prescription_creation(self, patient, doctor_user):
        consultation = Consultation.objects.create(
            patient=patient,
            doctor=doctor_user,
            symptoms="Douleurs abdominales.",
            diagnosis="Gastro-entérite aiguë",
        )
        prescription = Prescription.objects.create(
            consultation=consultation,
            patient=patient,
            doctor=doctor_user,
        )
        assert prescription.code.startswith("RX-")
        PrescriptionItem.objects.create(
            prescription=prescription,
            medication_name="Paracétamol",
            dosage="1g trois fois par jour",
            duration="5 jours",
            quantity=15,
        )
        assert prescription.items.count() == 1


@pytest.mark.django_db
class TestConsultationListView:
    def test_unauthenticated_redirect(self, client):
        url = reverse('consultations:consultation_list')
        resp = client.get(url)
        assert resp.status_code == 302
        assert '/accounts/' in resp['Location'] or 'login' in resp['Location']

    def test_doctor_sees_only_own(self, client, doctor_user, patient, admin_user):
        # Create consultation for this doctor
        Consultation.objects.create(
            patient=patient, doctor=doctor_user,
            symptoms="S", diagnosis="D1",
        )
        # Create consultation for another doctor - use admin_user as second doctor
        from apps.accounts.models import User
        other_doc = User.objects.create_user(
            username="dr_other", password="pass1234!",
            role="DOCTOR", first_name="Other", last_name="Doc"
        )
        Consultation.objects.create(
            patient=patient, doctor=other_doc,
            symptoms="S", diagnosis="D2",
        )

        client.force_login(doctor_user)
        resp = client.get(reverse('consultations:consultation_list'))
        assert resp.status_code == 200
        consultations = resp.context['consultations']
        # Doctor should only see their own
        for c in consultations:
            assert c.doctor == doctor_user

    def test_admin_sees_all(self, client, admin_user, patient, doctor_user):
        Consultation.objects.create(patient=patient, doctor=doctor_user, symptoms="S", diagnosis="D1")
        client.force_login(admin_user)
        resp = client.get(reverse('consultations:consultation_list'))
        assert resp.status_code == 200
        assert resp.context['consultations'].count() >= 1


@pytest.mark.django_db
class TestPrescriptionPDFView:
    def test_pdf_view_fallback(self, client, doctor_user, patient):
        consultation = Consultation.objects.create(
            patient=patient, doctor=doctor_user, symptoms="S", diagnosis="D"
        )
        prescription = Prescription.objects.create(
            consultation=consultation, patient=patient, doctor=doctor_user,
        )
        client.force_login(doctor_user)
        resp = client.get(reverse('consultations:prescription_pdf', kwargs={'pk': prescription.pk}))
        # WeasyPrint may not be available in test env; should fallback to HTML 200
        assert resp.status_code == 200
