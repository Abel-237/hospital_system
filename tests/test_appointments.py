import pytest
from datetime import date, time
from django.urls import reverse
from apps.appointments.models import Appointment

@pytest.mark.django_db
def test_appointment_booking_and_queue(client, doctor_user, patient_record):
    today = date.today()
    slot = time(10, 0)
    
    appt = Appointment.objects.create(
        patient=patient_record,
        doctor=doctor_user,
        scheduled_date=today,
        scheduled_time=slot,
        reason='Checkup',
        status=Appointment.Status.SCHEDULED
    )
    assert appt.status == Appointment.Status.SCHEDULED

    # Simulate transition to WAITING (Arrival)
    client.force_login(doctor_user)
    status_url = reverse('appointments:update_status', kwargs={'pk': appt.pk})
    resp = client.post(status_url, {'status': 'WAITING'})
    
    appt.refresh_from_db()
    assert appt.status == Appointment.Status.WAITING
    assert appt.arrival_time is not None
    assert appt.queue_number == 1
