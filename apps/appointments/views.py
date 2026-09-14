from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse
from .models import Appointment
from .forms import AppointmentForm

class AppointmentListView(LoginRequiredMixin, ListView):
    model = Appointment
    template_name = 'appointments/appointment_list.html'
    context_object_name = 'appointments'
    paginate_by = 20

    def get_queryset(self):
        qs = Appointment.objects.select_related('patient', 'doctor').all()
        selected_date = self.request.GET.get('date', '')
        status = self.request.GET.get('status', '')
        
        if selected_date:
            qs = qs.filter(scheduled_date=selected_date)
        else:
            qs = qs.filter(scheduled_date=timezone.now().date())
            
        if status:
            qs = qs.filter(status=status)
            
        # Object-level filtering for doctors
        if self.request.user.role == 'DOCTOR':
            qs = qs.filter(doctor=self.request.user)
            
        return qs.order_by('scheduled_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_date'] = self.request.GET.get('date', str(timezone.now().date()))
        context['statuses'] = Appointment.Status.choices
        context['selected_status'] = self.request.GET.get('status', '')
        return context


class AppointmentCreateView(LoginRequiredMixin, CreateView):
    model = Appointment
    form_class = AppointmentForm
    template_name = 'appointments/appointment_form.html'

    def form_valid(self, form):
        appointment = form.save(commit=False)
        appointment.created_by = self.request.user
        appointment.save()
        messages.success(self.request, _("Rendez-vous programmé avec succès pour %(patient)s.") % {'patient': appointment.patient.full_name})
        return redirect('appointments:appointment_list')


class WaitingQueueBoardView(LoginRequiredMixin, View):
    """
    Live real-time HTMX waiting room queue board.
    Categorized into: Attente (WAITING), En consultation (IN_CONSULTATION), Terminé (COMPLETED).
    """
    def get(self, request):
        today = timezone.now().date()
        qs = Appointment.objects.filter(scheduled_date=today).select_related('patient', 'doctor')
        
        if request.user.role == 'DOCTOR':
            qs = qs.filter(doctor=request.user)
            
        waiting = qs.filter(status='WAITING').order_by('arrival_time', 'scheduled_time')
        in_consultation = qs.filter(status='IN_CONSULTATION').order_by('scheduled_time')
        completed = qs.filter(status='COMPLETED').order_by('-updated_at')[:10]
        scheduled = qs.filter(status='SCHEDULED').order_by('scheduled_time')

        context = {
            'today': today,
            'waiting': waiting,
            'in_consultation': in_consultation,
            'completed': completed,
            'scheduled': scheduled,
        }

        if request.headers.get('HX-Request'):
            return render(request, 'appointments/_queue_board_partial.html', context)
        return render(request, 'appointments/queue_board.html', context)


class UpdateAppointmentStatusView(LoginRequiredMixin, View):
    """
    HTMX action to transition appointment state:
    SCHEDULED -> WAITING (Patient arrived at reception)
    WAITING -> IN_CONSULTATION (Doctor calls patient into room)
    IN_CONSULTATION -> COMPLETED (Consultation finished)
    """
    def post(self, request, pk):
        appointment = get_object_or_404(Appointment, pk=pk)
        new_status = request.POST.get('status')
        
        if new_status in Appointment.Status.values:
            appointment.status = new_status
            if new_status == Appointment.Status.WAITING and not appointment.arrival_time:
                appointment.arrival_time = timezone.now()
                # compute sequential queue number of the day
                count_today = Appointment.objects.filter(
                    scheduled_date=appointment.scheduled_date,
                    queue_number__isnull=False
                ).count()
                appointment.queue_number = count_today + 1
            appointment.save()

        # If HTMX request, redirect back or render fresh queue snippet
        if request.headers.get('HX-Request'):
            response = HttpResponse()
            response['HX-Trigger'] = 'queueUpdated'
            return response
            
        return redirect('appointments:queue_board')
