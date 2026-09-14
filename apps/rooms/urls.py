from django.urls import path
from .views import (
    BedMatrixView, AdmissionCreateView, AdmissionDetailView,
    DischargeAdmissionView, NursingNoteCreateView
)

app_name = 'rooms'

urlpatterns = [
    path('', BedMatrixView.as_view(), name='bed_matrix'),
    path('admission/create/', AdmissionCreateView.as_view(), name='admission_create'),
    path('admission/<int:pk>/', AdmissionDetailView.as_view(), name='admission_detail'),
    path('admission/<int:pk>/discharge/', DischargeAdmissionView.as_view(), name='discharge'),
    path('admission/<int:admission_id>/note/create/', NursingNoteCreateView.as_view(), name='note_create'),
]
