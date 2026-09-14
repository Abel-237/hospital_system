import pytest
from rest_framework.test import APIClient
from django.urls import reverse

@pytest.mark.django_db
def test_api_patient_endpoints(doctor_user, patient_record):
    api_client = APIClient()
    api_client.force_authenticate(user=doctor_user)

    url = reverse('api:api_patient-list')
    response = api_client.get(url)
    assert response.status_code == 200
    assert response.data['count'] >= 1
    assert response.data['results'][0]['matricule'] == patient_record.matricule

@pytest.mark.django_db
def test_api_unauthenticated_blocked():
    api_client = APIClient()
    url = reverse('api:api_patient-list')
    response = api_client.get(url)
    assert response.status_code == 403 or response.status_code == 401
