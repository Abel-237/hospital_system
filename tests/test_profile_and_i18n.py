import io
import pytest
from PIL import Image
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.accounts.models import User

def create_test_image(format='PNG', size=(100, 100), color=(0, 128, 255)):
    file_obj = io.BytesIO()
    image = Image.new('RGB', size, color)
    image.save(file_obj, format=format)
    file_obj.seek(0)
    return file_obj.getvalue()

@pytest.mark.django_db
def test_profile_view_get(client, doctor_user):
    client.force_login(doctor_user)
    url = reverse('accounts:profile')
    response = client.get(url)
    assert response.status_code == 200
    assert doctor_user.display_title.encode('utf-8') in response.content or doctor_user.username.encode('utf-8') in response.content
    assert doctor_user.initials in response.content.decode('utf-8')

@pytest.mark.django_db
def test_profile_view_post_update_fields(client, doctor_user):
    client.force_login(doctor_user)
    url = reverse('accounts:profile')
    data = {
        'first_name': 'Paul-Emmanuel',
        'last_name': 'Kamgaing',
        'email': 'dr.kamgaing@hospital-cmr.local',
        'phone_number': '+237 671 22 33 44',
        'speciality': 'Cardiologue Interventionnel',
        'license_number': 'ONMC-2026-100',
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('accounts:profile')

    doctor_user.refresh_from_db()
    assert doctor_user.first_name == 'Paul-Emmanuel'
    assert doctor_user.last_name == 'Kamgaing'
    assert doctor_user.email == 'dr.kamgaing@hospital-cmr.local'
    assert doctor_user.phone_number == '+237 671 22 33 44'
    assert doctor_user.speciality == 'Cardiologue Interventionnel'
    assert doctor_user.license_number == 'ONMC-2026-100'

@pytest.mark.django_db
def test_profile_avatar_upload(client, doctor_user):
    client.force_login(doctor_user)
    url = reverse('accounts:profile')
    
    img_bytes = create_test_image(format='PNG')
    uploaded_avatar = SimpleUploadedFile(
        'my_avatar.png',
        img_bytes,
        content_type='image/png'
    )

    data = {
        'first_name': doctor_user.first_name,
        'last_name': doctor_user.last_name,
        'email': doctor_user.email,
        'phone_number': doctor_user.phone_number,
        'speciality': doctor_user.speciality,
        'license_number': doctor_user.license_number,
        'avatar': uploaded_avatar,
    }
    response = client.post(url, data)
    assert response.status_code == 302

    doctor_user.refresh_from_db()
    assert doctor_user.avatar is not None
    assert 'avatars/' in doctor_user.avatar.name
    assert doctor_user.avatar_url is not None
    assert 'media/avatars/' in doctor_user.avatar_url

@pytest.mark.django_db
def test_profile_avatar_remove(client, doctor_user):
    client.force_login(doctor_user)
    url = reverse('accounts:profile')
    
    # 1. First upload an avatar
    img_bytes = create_test_image(format='JPEG')
    uploaded_avatar = SimpleUploadedFile('doc.jpg', img_bytes, content_type='image/jpeg')
    doctor_user.avatar = uploaded_avatar
    doctor_user.save()
    assert doctor_user.avatar_url is not None

    # 2. Post with remove_avatar = True
    data = {
        'first_name': doctor_user.first_name,
        'last_name': doctor_user.last_name,
        'email': doctor_user.email,
        'phone_number': doctor_user.phone_number,
        'speciality': doctor_user.speciality,
        'license_number': doctor_user.license_number,
        'remove_avatar': 'true',
    }
    response = client.post(url, data)
    assert response.status_code == 302

    doctor_user.refresh_from_db()
    assert not doctor_user.avatar
    assert doctor_user.avatar_url is None

@pytest.mark.django_db
def test_profile_avatar_oversized_validation(client, doctor_user):
    client.force_login(doctor_user)
    url = reverse('accounts:profile')

    import os
    img = Image.new('RGB', (1000, 1000))
    img.frombytes(os.urandom(1000 * 1000 * 3))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    huge_file = SimpleUploadedFile('huge.png', buf.getvalue(), content_type='image/png')

    data = {
        'first_name': doctor_user.first_name,
        'last_name': doctor_user.last_name,
        'email': doctor_user.email,
        'phone_number': doctor_user.phone_number,
        'speciality': doctor_user.speciality,
        'license_number': doctor_user.license_number,
        'avatar': huge_file,
    }
    response = client.post(url, data)
    assert response.status_code == 200
    assert "trop volumineux" in response.content.decode('utf-8')

@pytest.mark.django_db
def test_profile_avatar_invalid_format_validation(client, doctor_user):
    client.force_login(doctor_user)
    url = reverse('accounts:profile')

    buf = io.BytesIO()
    img = Image.new('RGB', (50, 50), (255, 0, 0))
    img.save(buf, format='BMP')
    invalid_file = SimpleUploadedFile('photo.bmp', buf.getvalue(), content_type='image/bmp')
    
    data = {
        'first_name': doctor_user.first_name,
        'last_name': doctor_user.last_name,
        'email': doctor_user.email,
        'phone_number': doctor_user.phone_number,
        'speciality': doctor_user.speciality,
        'license_number': doctor_user.license_number,
        'avatar': invalid_file,
    }
    response = client.post(url, data)
    assert response.status_code == 200
    assert "non supporté" in response.content.decode('utf-8')

@pytest.mark.django_db
def test_i18n_language_switching(client, doctor_user):
    client.force_login(doctor_user)

    # 1. Switch to English
    switch_url = reverse('set_language')
    response = client.post(switch_url, {'language': 'en', 'next': '/dashboard/'}, follow=True)
    assert response.status_code == 200
    content_en = response.content.decode('utf-8')
    assert "Dashboard" in content_en
    assert "Sign Out" in content_en or "Electronic Health" in content_en

    # 2. Switch back to French
    response = client.post(switch_url, {'language': 'fr', 'next': '/dashboard/'}, follow=True)
    assert response.status_code == 200
    content_fr = response.content.decode('utf-8')
    assert "Tableau de Bord" in content_fr or "Tableau de bord" in content_fr
    assert "Déconnexion" in content_fr or "Se Déconnecter" in content_fr
