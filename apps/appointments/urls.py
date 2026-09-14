from django.urls import path
from .views import (
    AppointmentListView, AppointmentCreateView,
    WaitingQueueBoardView, UpdateAppointmentStatusView
)

app_name = 'appointments'

urlpatterns = [
    path('', AppointmentListView.as_view(), name='appointment_list'),
    path('create/', AppointmentCreateView.as_view(), name='appointment_create'),
    path('queue/', WaitingQueueBoardView.as_view(), name='queue_board'),
    path('<int:pk>/status/', UpdateAppointmentStatusView.as_view(), name='update_status'),
]
