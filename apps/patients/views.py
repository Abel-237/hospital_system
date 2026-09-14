from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _
from apps.core.permissions import RoleRequiredMixin
from .models import Patient
from .forms import PatientForm

class PatientListView(LoginRequiredMixin, ListView):
    model = Patient
    template_name = 'patients/patient_list.html'
    context_object_name = 'patients'
    paginate_by = 15

    def get_queryset(self):
        qs = Patient.objects.all().order_by('-created_at')
        query = self.request.GET.get('q', '').strip()
        blood_group = self.request.GET.get('blood_group', '').strip()

        if query:
            qs = qs.filter(
                Q(matricule__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(phone__icontains=query)
            )
        if blood_group:
            qs = qs.filter(blood_group=blood_group)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['blood_group'] = self.request.GET.get('blood_group', '')
        context['blood_groups'] = Patient.BloodGroup.choices
        return context

    def render_to_response(self, context, **response_kwargs):
        # HTMX instant search partial render
        if self.request.headers.get('HX-Request') and not self.request.headers.get('HX-Boosted'):
            return render(self.request, 'patients/_table.html', context)
        return super().render_to_response(context, **response_kwargs)


class PatientDetailView(LoginRequiredMixin, DetailView):
    model = Patient
    template_name = 'patients/patient_detail.html'
    context_object_name = 'patient'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.object

        # Fetch related patient timeline events
        context['consultations'] = patient.consultations.all().order_by('-created_at') if hasattr(patient, 'consultations') else []
        context['appointments'] = patient.appointments.all().order_by('-scheduled_date', '-scheduled_time') if hasattr(patient, 'appointments') else []
        context['admissions'] = patient.admissions.all().order_by('-admission_date') if hasattr(patient, 'admissions') else []
        context['invoices'] = patient.invoices.all().order_by('-created_at') if hasattr(patient, 'invoices') else []
        context['audit_logs'] = patient.history.all()[:5]
        return context


class PatientCreateView(LoginRequiredMixin, CreateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patients/patient_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Enregistrer un nouveau Patient")
        return context

    def form_valid(self, form):
        patient = form.save()
        messages.success(self.request, _("Dossier patient créé avec succès. Matricule: %(matricule)s") % {'matricule': patient.matricule})
        return redirect('patients:patient_detail', pk=patient.pk)


class PatientUpdateView(LoginRequiredMixin, UpdateView):
    model = Patient
    form_class = PatientForm
    template_name = 'patients/patient_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("Modifier le Dossier Patient")
        context['patient'] = self.object
        return context

    def form_valid(self, form):
        patient = form.save()
        messages.success(self.request, _("Dossier patient %(matricule)s mis à jour avec succès.") % {'matricule': patient.matricule})
        return redirect('patients:patient_detail', pk=patient.pk)


class PatientHistoryAuditView(RoleRequiredMixin, View):
    """
    Detailed audit log of all changes made to a patient's medical record.
    Accessible to Administrators, Doctors, and Compliance officers.
    """
    allowed_roles = ['ADMIN', 'DOCTOR']

    def get(self, request, pk):
        patient = get_object_or_404(Patient, pk=pk)
        history_records = patient.history.all().order_by('-history_date')
        return render(request, 'patients/patient_history.html', {
            'patient': patient,
            'history_records': history_records,
        })
