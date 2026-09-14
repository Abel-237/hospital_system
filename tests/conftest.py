# tests/conftest.py
import pytest
from datetime import date, time, timedelta
from django.utils import timezone
from apps.accounts.models import User
from apps.patients.models import Patient
from apps.appointments.models import Appointment
from apps.pharmacy.models import Medication, StockBatch
from apps.billing.models import Invoice, InvoiceItem, Payment, InsurancePolicy

@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username='admin',
        email='admin@hospital-cmr.local',
        password='password123',
        role=User.Role.ADMIN,
        first_name='Admin',
        last_name='Système'
    )

@pytest.fixture
def doctor_user(db):
    user = User.objects.create_user(
        username='dr.kamga',
        email='dr.kamga@hospital-cmr.local',
        password='password123',
        role=User.Role.DOCTOR,
        first_name='Paul',
        last_name='Kamga',
        speciality='Cardiologie',
        license_number='ONMC-2026-99'
    )
    return user

@pytest.fixture
def nurse_user(db):
    return User.objects.create_user(
        username='inf.marie',
        email='inf.marie@hospital-cmr.local',
        password='password123',
        role=User.Role.NURSE,
        first_name='Marie',
        last_name='Ngo'
    )

@pytest.fixture
def pharmacist_user(db):
    return User.objects.create_user(
        username='pharm.alain',
        email='pharm.alain@hospital-cmr.local',
        password='password123',
        role=User.Role.PHARMACIST,
        first_name='Alain',
        last_name='Fosso'
    )

@pytest.fixture
def cashier_user(db):
    return User.objects.create_user(
        username='caisse.alice',
        email='caisse.alice@hospital-cmr.local',
        password='password123',
        role=User.Role.CASHIER,
        first_name='Alice',
        last_name='Bella'
    )

@pytest.fixture
def patient_record(db):
    return Patient.objects.create(
        matricule='CMR-2026-TEST01',
        first_name='Samuel',
        last_name='Eto',
        birth_date=date(1990, 5, 15),
        gender=Patient.Gender.MALE,
        blood_group=Patient.BloodGroup.O_POS,
        phone='+237670000001',
        city='Douala',
        consent_given=True,
        consent_given_at=timezone.now()
    )

@pytest.fixture
def patient(patient_record):
    """Alias for patient_record — kept for backward compatibility with tests."""
    return patient_record
