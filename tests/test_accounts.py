import pytest
from django.urls import reverse
from apps.accounts.models import User

@pytest.mark.django_db
def test_user_roles(doctor_user, nurse_user, cashier_user):
    assert doctor_user.role == User.Role.DOCTOR
    assert doctor_user.display_title == "Dr. Paul Kamga"
    assert nurse_user.role == User.Role.NURSE
    assert cashier_user.role == User.Role.CASHIER
    assert doctor_user.is_2fa_mandatory() is True
    assert nurse_user.is_2fa_mandatory() is False

@pytest.mark.django_db
def test_login_flow(client, doctor_user):
    url = reverse('accounts:login')
    response = client.get(url)
    assert response.status_code == 200

    # Successful login
    response = client.post(url, {'username': 'dr.kamga', 'password': 'password123'})
    assert response.status_code == 302
    assert response.url == reverse('core:dashboard')

@pytest.mark.django_db
def test_rbac_access_control(client, nurse_user):
    client.force_login(nurse_user)
    # Nurses are not allowed on staff creation
    staff_create_url = reverse('accounts:staff_create')
    response = client.get(staff_create_url)
    assert response.status_code == 403
