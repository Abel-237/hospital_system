from urllib.parse import urlsplit, urlunsplit
from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect, render
from django.urls import translate_url
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import check_for_language, get_language_from_path, override
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.db.models import Count, Sum, Q, F


def custom_set_language(request):
    """
    Language switcher view with robust URL prefix handling for i18n_patterns.
    Correctly translates between prefixed (/en/...) and non-prefixed default (/...) paths.
    """
    next_url = request.POST.get("next", request.GET.get("next"))
    if (
        (next_url or request.accepts("text/html"))
        and not url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        )
    ):
        next_url = request.META.get("HTTP_REFERER")
        if not url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            next_url = "/"

    response = HttpResponseRedirect(next_url) if next_url else HttpResponse(status=204)

    if request.method == "POST":
        lang_code = request.POST.get("language")
        if lang_code and check_for_language(lang_code):
            if next_url:
                current_url_lang = get_language_from_path(urlsplit(next_url).path) or settings.LANGUAGE_CODE
                with override(current_url_lang):
                    next_trans = translate_url(next_url, lang_code)
                if next_trans != next_url:
                    response = HttpResponseRedirect(next_trans)
                else:
                    # Fallback prefix adjustment if translate_url didn't transform
                    parsed = urlsplit(next_url)
                    path = parsed.path
                    if lang_code == settings.LANGUAGE_CODE and current_url_lang != settings.LANGUAGE_CODE:
                        prefix = f"/{current_url_lang}/"
                        if path.startswith(prefix):
                            path = "/" + path[len(prefix):]
                            response = HttpResponseRedirect(urlunsplit((parsed.scheme, parsed.netloc, path, parsed.query, parsed.fragment)))
                    elif lang_code != settings.LANGUAGE_CODE and current_url_lang == settings.LANGUAGE_CODE:
                        path = f"/{lang_code}" + (path if path.startswith("/") else f"/{path}")
                        response = HttpResponseRedirect(urlunsplit((parsed.scheme, parsed.netloc, path, parsed.query, parsed.fragment)))

            response.set_cookie(
                settings.LANGUAGE_COOKIE_NAME,
                lang_code,
                max_age=settings.LANGUAGE_COOKIE_AGE,
                path=settings.LANGUAGE_COOKIE_PATH,
                domain=settings.LANGUAGE_COOKIE_DOMAIN,
                secure=settings.LANGUAGE_COOKIE_SECURE,
                httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
                samesite=settings.LANGUAGE_COOKIE_SAMESITE,
            )

    return response


class RootRedirectView(View):
    """
    Redirect incoming root requests:
    - Logged-in users -> role-specific dashboard
    - Anonymous users -> login page
    """
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return redirect('accounts:login')


class HealthCheckView(View):
    """
    Service health check for load balancers and container probes.
    """
    def get(self, request, *args, **kwargs):
        return JsonResponse({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'service': 'hospital_system',
            'version': '2026.1',
        })


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Central dispatch dashboard view adapting to user role.
    """
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        role = getattr(user, 'role', 'ADMIN')
        today = timezone.now().date()

        # Import models dynamically to prevent early circular imports
        from apps.patients.models import Patient
        from apps.appointments.models import Appointment
        from apps.consultations.models import Consultation, VitalSigns
        from apps.pharmacy.models import Medication, Dispensation
        from apps.laboratory.models import LabOrder
        from apps.rooms.models import Bed, Admission
        from apps.billing.models import Invoice, Payment

        context['role'] = role
        context['today'] = today

        # Universal KPIs
        context['total_patients'] = Patient.objects.count()
        context['today_appointments_count'] = Appointment.objects.filter(scheduled_date=today).count()
        
        # Bed occupancy rate
        total_beds = Bed.objects.count()
        occupied_beds = Bed.objects.filter(status='OCCUPIED').count()
        context['total_beds'] = total_beds
        context['occupied_beds'] = occupied_beds
        context['occupancy_rate'] = round((occupied_beds / total_beds * 100) if total_beds > 0 else 0, 1)

        # Role-specific dashboard payloads
        if role == 'DOCTOR':
            context['my_appointments'] = Appointment.objects.filter(
                doctor=user, scheduled_date=today
            ).order_by('scheduled_time')
            context['waiting_patients'] = Appointment.objects.filter(
                doctor=user, scheduled_date=today, status='WAITING'
            )
            context['recent_consultations'] = Consultation.objects.filter(
                doctor=user
            ).order_by('-created_at')[:5]
            context['pending_lab_results'] = LabOrder.objects.filter(
                consultation__doctor=user, status='COMPLETED'
            )[:5]

        elif role == 'NURSE':
            context['waiting_queue'] = Appointment.objects.filter(
                scheduled_date=today, status='WAITING'
            ).order_by('scheduled_time')
            context['active_admissions'] = Admission.objects.filter(
                discharge_date__isnull=True
            ).select_related('patient', 'bed')[:10]
            context['recent_vitals'] = VitalSigns.objects.order_by('-created_at')[:5]

        elif role == 'PHARMACIST':
            context['low_stock_medications'] = Medication.objects.filter(
                current_stock__lte=F('critical_stock_threshold')
            )[:10] if hasattr(Medication, 'current_stock') else []
            context['pending_dispensations'] = Dispensation.objects.filter(
                status='PENDING'
            ).order_by('-created_at')[:10]
            context['today_dispensed_count'] = Dispensation.objects.filter(
                dispensed_at__date=today
            ).count()

        elif role == 'LABORANT':
            context['pending_lab_orders'] = LabOrder.objects.filter(
                status__in=['PENDING', 'IN_PROGRESS']
            ).order_by('-created_at')[:10]
            context['completed_orders_today'] = LabOrder.objects.filter(
                completed_at__date=today
            ).count()

        elif role == 'CASHIER':
            today_payments = Payment.objects.filter(created_at__date=today, status='SUCCESS')
            context['today_revenue'] = today_payments.aggregate(total=Sum('amount'))['total'] or 0
            context['today_orange_money'] = today_payments.filter(method='ORANGE_MONEY').aggregate(total=Sum('amount'))['total'] or 0
            context['today_mtn_momo'] = today_payments.filter(method='MTN_MOMO').aggregate(total=Sum('amount'))['total'] or 0
            context['today_cash'] = today_payments.filter(method='CASH').aggregate(total=Sum('amount'))['total'] or 0
            context['pending_invoices'] = Invoice.objects.filter(status='PENDING').order_by('-created_at')[:10]

        elif role in ['ADMIN', 'RECEPTIONIST']:
            today_payments = Payment.objects.filter(created_at__date=today, status='SUCCESS')
            context['today_revenue'] = today_payments.aggregate(total=Sum('amount'))['total'] or 0
            context['recent_patients'] = Patient.objects.order_by('-created_at')[:5]
            context['recent_admissions'] = Admission.objects.filter(discharge_date__isnull=True)[:5]
            context['all_today_appointments'] = Appointment.objects.filter(scheduled_date=today).order_by('scheduled_time')[:10]

        return context
