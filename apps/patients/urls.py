from django.urls import path
from .views import (
    PatientListView, PatientDetailView, PatientCreateView,
    PatientUpdateView, PatientHistoryAuditView
)

app_name = 'patients'

urlpatterns = [
    path('', PatientListView.as_view(), name='patient_list'),
    path('create/', PatientCreateView.as_view(), name='patient_create'),
    path('<uuid:pk>/', PatientDetailView.as_view(), name='patient_detail'),
    path('<uuid:pk>/edit/', PatientUpdateView.as_view(), name='patient_update'),
    path('<uuid:pk>/audit-history/', PatientHistoryAuditView.as_view(), name='patient_history'),
]
