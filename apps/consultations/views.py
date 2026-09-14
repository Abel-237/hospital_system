import io
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.core.permissions import RoleRequiredMixin
from apps.patients.models import Patient
from apps.appointments.models import Appointment
from .models import Consultation, VitalSigns, Prescription, PrescriptionItem
from .forms import VitalSignsForm, ConsultationForm, PrescriptionItemFormSet


class ConsultationListView(LoginRequiredMixin, ListView):
    """
    List of all consultations with role-based filtering:
    - Doctors see only their own consultations
    - Other roles see all consultations
    """
    model = Consultation
    template_name = 'consultations/consultation_list.html'
    context_object_name = 'consultations'
    paginate_by = 20

    def get_queryset(self):
        qs = Consultation.objects.select_related('patient', 'doctor', 'vital_signs').order_by('-created_at')
        user = self.request.user
        if user.role == 'DOCTOR' and not user.is_superuser:
            qs = qs.filter(doctor=user)
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(
                Q(patient__first_name__icontains=q) |
                Q(patient__last_name__icontains=q) |
                Q(patient__matricule__icontains=q) |
                Q(diagnosis__icontains=q)
            )
        date_filter = self.request.GET.get('date', '')
        if date_filter:
            qs = qs.filter(created_at__date=date_filter)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['date_filter'] = self.request.GET.get('date', '')
        context['today'] = timezone.now().date()
        return context

class VitalSignsCreateView(RoleRequiredMixin, CreateView):
    model = VitalSigns
    form_class = VitalSignsForm
    template_name = 'consultations/vital_signs_form.html'
    allowed_roles = ['NURSE', 'DOCTOR', 'ADMIN']

    def get_initial(self):
        initial = super().get_initial()
        patient_id = self.request.GET.get('patient')
        if patient_id:
            initial['patient'] = get_object_or_404(Patient, pk=patient_id)
        return initial

    def form_valid(self, form):
        vitals = form.save(commit=False)
        vitals.recorded_by = self.request.user
        vitals.save()
        messages.success(self.request, _("Constantes vitales enregistrées avec succès pour %(patient)s.") % {'patient': vitals.patient.full_name})
        
        # If created from an appointment queue
        appointment_id = self.request.GET.get('appointment')
        if appointment_id:
            return redirect('appointments:queue_board')
        return redirect('patients:patient_detail', pk=vitals.patient.pk)


class ConsultationCreateView(RoleRequiredMixin, View):
    allowed_roles = ['DOCTOR', 'ADMIN']

    def get(self, request, patient_id):
        patient = get_object_or_404(Patient, pk=patient_id)
        appointment_id = request.GET.get('appointment')
        appointment = get_object_or_404(Appointment, pk=appointment_id) if appointment_id else None
        
        # Look for the latest vitals recorded today
        latest_vitals = VitalSigns.objects.filter(patient=patient).order_by('-created_at').first()
        form = ConsultationForm(initial={'vital_signs': latest_vitals})
        
        return render(request, 'consultations/consultation_form.html', {
            'patient': patient,
            'appointment': appointment,
            'form': form,
            'latest_vitals': latest_vitals,
        })

    def post(self, request, patient_id):
        patient = get_object_or_404(Patient, pk=patient_id)
        form = ConsultationForm(request.POST)
        appointment_id = request.GET.get('appointment')
        appointment = get_object_or_404(Appointment, pk=appointment_id) if appointment_id else None

        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.patient = patient
            consultation.doctor = request.user
            if appointment:
                consultation.appointment = appointment
                appointment.status = Appointment.Status.COMPLETED
                appointment.save()
            consultation.save()
            
            messages.success(request, _("Consultation enregistrée avec succès."))
            return redirect('consultations:consultation_detail', pk=consultation.pk)
            
        return render(request, 'consultations/consultation_form.html', {
            'patient': patient,
            'appointment': appointment,
            'form': form,
        })


class ConsultationDetailView(LoginRequiredMixin, DetailView):
    model = Consultation
    template_name = 'consultations/consultation_detail.html'
    context_object_name = 'consultation'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['prescriptions'] = self.object.prescriptions.all().prefetch_related('items')
        context['lab_orders'] = self.object.lab_orders.all() if hasattr(self.object, 'lab_orders') else []
        return context


class PrescriptionCreateView(RoleRequiredMixin, View):
    allowed_roles = ['DOCTOR', 'ADMIN']

    def get(self, request, consultation_id):
        consultation = get_object_or_404(Consultation, pk=consultation_id)
        prescription = Prescription(consultation=consultation, patient=consultation.patient, doctor=request.user)
        formset = PrescriptionItemFormSet(instance=prescription)
        return render(request, 'consultations/prescription_form.html', {
            'consultation': consultation,
            'formset': formset,
        })

    def post(self, request, consultation_id):
        consultation = get_object_or_404(Consultation, pk=consultation_id)
        prescription = Prescription(
            consultation=consultation,
            patient=consultation.patient,
            doctor=request.user,
            notes=request.POST.get('notes', '')
        )
        formset = PrescriptionItemFormSet(request.POST, instance=prescription)
        
        if formset.is_valid():
            prescription.save()
            formset.save()
            messages.success(request, _("Ordonnance numérique n°%(code)s générée avec succès.") % {'code': prescription.code})
            return redirect('consultations:consultation_detail', pk=consultation.pk)
            
        return render(request, 'consultations/prescription_form.html', {
            'consultation': consultation,
            'formset': formset,
        })


class PrescriptionPDFView(LoginRequiredMixin, View):
    """
    Generate official PDF prescription using WeasyPrint with fallback to print view.
    """
    def get(self, request, pk):
        prescription = get_object_or_404(
            Prescription.objects.select_related('patient', 'doctor', 'consultation'),
            pk=pk
        )
        html_string = render_to_string('pdf/prescription.html', {
            'prescription': prescription,
            'patient': prescription.patient,
            'doctor': prescription.doctor,
            'items': prescription.items.all(),
        }, request=request)

        # Attempt WeasyPrint conversion
        try:
            import weasyprint
            pdf_file = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="Ordonnance_{prescription.code}.pdf"'
            return response
        except Exception:
            # Fallback printable HTML
            return HttpResponse(html_string)
