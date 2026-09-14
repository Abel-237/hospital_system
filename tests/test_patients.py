import pytest
from datetime import date
from django.urls import reverse
from apps.patients.models import Patient

@pytest.mark.django_db
def test_patient_auto_matricule(patient_record):
    assert patient_record.matricule.startswith("CMR-")
    assert patient_record.full_name == "Samuel Eto"
    assert patient_record.age == date.today().year - 1990

@pytest.mark.django_db
def test_patient_audit_history(patient_record):
    # Modify patient and check historical record creation
    patient_record.city = 'Yaoundé'
    patient_record.save()

    history = patient_record.history.all()
    assert history.count() >= 2
    latest = history.first()
    assert latest.city == 'Yaoundé'

@pytest.mark.django_db
def test_patient_search_htmx(client, doctor_user, patient_record):
    client.force_login(doctor_user)
    url = reverse('patients:patient_list')
    
    # Standard request
    resp = client.get(url, {'q': 'Samuel'})
    assert resp.status_code == 200
    assert 'Samuel Eto' in resp.content.decode()

    # HTMX partial request
    htmx_resp = client.get(url, {'q': 'TEST01'}, HTTP_HX_REQUEST='true')
    assert htmx_resp.status_code == 200
    assert 'patient-table-container' in htmx_resp.content.decode()
