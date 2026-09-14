from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.core.permissions import RoleRequiredMixin
from apps.patients.models import Patient
from .models import Ward, Room, Bed, Admission, NursingNote
from .forms import AdmissionForm, DischargeForm, NursingNoteForm

class BedMatrixView(LoginRequiredMixin, View):
    """
    Visual hospital floor plan and bed occupancy dashboard.
    """
    def get(self, request):
        wards = Ward.objects.prefetch_related('rooms__beds').all()
        total_beds = Bed.objects.count()
        occupied_beds = Bed.objects.filter(status=Bed.Status.OCCUPIED).count()
        available_beds = Bed.objects.filter(status=Bed.Status.AVAILABLE).count()
        maintenance_beds = Bed.objects.filter(status=Bed.Status.MAINTENANCE).count()

        context = {
            'wards': wards,
            'total_beds': total_beds,
            'occupied_beds': occupied_beds,
            'available_beds': available_beds,
            'maintenance_beds': maintenance_beds,
            'occupancy_rate': round((occupied_beds / total_beds * 100) if total_beds > 0 else 0, 1),
        }
        return render(request, 'rooms/bed_matrix.html', context)


class AdmissionCreateView(RoleRequiredMixin, View):
    allowed_roles = ['DOCTOR', 'NURSE', 'ADMIN']

    def get(self, request):
        initial = {}
        patient_id = request.GET.get('patient')
        bed_id = request.GET.get('bed')
        if patient_id:
            initial['patient'] = get_object_or_404(Patient, pk=patient_id)
        if bed_id:
            initial['bed'] = get_object_or_404(Bed, pk=bed_id)

        form = AdmissionForm(initial=initial)
        return render(request, 'rooms/admission_form.html', {'form': form})

    def post(self, request):
        form = AdmissionForm(request.POST)
        if form.is_valid():
            admission = form.save(commit=False)
            admission.admitting_doctor = request.user if request.user.role == 'DOCTOR' else admission.patient.appointments.last().doctor if admission.patient.appointments.exists() else request.user
            admission.save()

            # Mark bed as occupied
            bed = admission.bed
            bed.status = Bed.Status.OCCUPIED
            bed.save()

            messages.success(request, _("Patient %(patient)s admis avec succès au lit %(bed)s.") % {
                'patient': admission.patient.full_name,
                'bed': str(bed)
            })
            return redirect('rooms:admission_detail', pk=admission.pk)
        return render(request, 'rooms/admission_form.html', {'form': form})


class AdmissionDetailView(LoginRequiredMixin, DetailView):
    model = Admission
    template_name = 'rooms/admission_detail.html'
    context_object_name = 'admission'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['notes'] = self.object.nursing_notes.select_related('nurse').all()
        context['note_form'] = NursingNoteForm()
        context['discharge_form'] = DischargeForm()
        return context


class DischargeAdmissionView(RoleRequiredMixin, View):
    allowed_roles = ['DOCTOR', 'ADMIN']

    def post(self, request, pk):
        admission = get_object_or_404(Admission, pk=pk)
        form = DischargeForm(request.POST)
        if form.is_valid():
            admission.discharge_summary = form.cleaned_data['discharge_summary']
            admission.discharge_date = timezone.now()
            admission.discharge_authorized_by = request.user
            admission.save()

            # Free bed
            bed = admission.bed
            bed.status = Bed.Status.AVAILABLE
            bed.save()

            messages.success(request, _("Sortie d’hospitalisation validée pour %(patient)s.") % {'patient': admission.patient.full_name})
            return redirect('rooms:bed_matrix')
        return redirect('rooms:admission_detail', pk=pk)


class NursingNoteCreateView(RoleRequiredMixin, View):
    allowed_roles = ['NURSE', 'DOCTOR', 'ADMIN']

    def post(self, request, admission_id):
        admission = get_object_or_404(Admission, pk=admission_id)
        form = NursingNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.admission = admission
            note.nurse = request.user
            note.save()
            messages.success(request, _("Transmission de soins enregistrée avec succès."))
        return redirect('rooms:admission_detail', pk=admission.pk)
