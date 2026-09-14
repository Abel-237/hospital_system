from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, F, Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.core.permissions import RoleRequiredMixin
from apps.consultations.models import Prescription
from .models import Medication, StockBatch, Dispensation, DispensationItem
from .forms import MedicationForm, StockBatchForm

class MedicationListView(LoginRequiredMixin, ListView):
    model = Medication
    template_name = 'pharmacy/medication_list.html'
    context_object_name = 'medications'
    paginate_by = 20

    def get_queryset(self):
        qs = Medication.objects.prefetch_related('batches').all()
        q = self.request.GET.get('q', '').strip()
        form = self.request.GET.get('form', '').strip()
        critical_only = self.request.GET.get('critical', '')

        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(dci__icontains=q))
        if form:
            qs = qs.filter(form=form)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        context['form_filter'] = self.request.GET.get('form', '')
        context['forms'] = Medication.Form.choices
        
        # Calculate expiring batches within 60 days
        today = timezone.now().date()
        sixty_days = today + timezone.timedelta(days=60)
        context['near_expiry_batches'] = StockBatch.objects.filter(
            expiration_date__gt=today,
            expiration_date__lte=sixty_days,
            quantity__gt=0
        ).select_related('medication')[:10]
        return context


class MedicationCreateView(RoleRequiredMixin, CreateView):
    model = Medication
    form_class = MedicationForm
    template_name = 'pharmacy/medication_form.html'
    allowed_roles = ['PHARMACIST', 'ADMIN']

    def form_valid(self, form):
        med = form.save()
        messages.success(self.request, _("Médicament %(name)s ajouté au livret thérapeutique.") % {'name': med.name})
        return redirect('pharmacy:medication_list')


class StockBatchCreateView(RoleRequiredMixin, CreateView):
    model = StockBatch
    form_class = StockBatchForm
    template_name = 'pharmacy/batch_form.html'
    allowed_roles = ['PHARMACIST', 'ADMIN']

    def get_initial(self):
        initial = super().get_initial()
        med_id = self.request.GET.get('medication')
        if med_id:
            initial['medication'] = get_object_or_404(Medication, pk=med_id)
        return initial

    def form_valid(self, form):
        batch = form.save()
        messages.success(self.request, _("Lot de stock %(batch)s enregistré avec succès.") % {'batch': batch.batch_number})
        return redirect('pharmacy:medication_list')


class PendingPrescriptionsView(RoleRequiredMixin, View):
    allowed_roles = ['PHARMACIST', 'ADMIN']

    def get(self, request):
        prescriptions = Prescription.objects.filter(
            is_dispensed=False
        ).select_related('patient', 'doctor').prefetch_related('items').order_by('-created_at')
        return render(request, 'pharmacy/pending_prescriptions.html', {'prescriptions': prescriptions})


class DispensePrescriptionView(RoleRequiredMixin, View):
    """
    Process prescription dispensation using FEFO (First-Expired, First-Out) batch allocation.
    """
    allowed_roles = ['PHARMACIST', 'ADMIN']

    def get(self, request, prescription_id):
        prescription = get_object_or_404(
            Prescription.objects.select_related('patient', 'doctor').prefetch_related('items'),
            pk=prescription_id
        )
        return render(request, 'pharmacy/dispense_confirm.html', {'prescription': prescription})

    def post(self, request, prescription_id):
        prescription = get_object_or_404(Prescription, pk=prescription_id)
        if prescription.is_dispensed:
            messages.warning(request, _("Cette ordonnance a déjà été délivrée."))
            return redirect('pharmacy:pending_prescriptions')

        today = timezone.now().date()
        dispensation = Dispensation.objects.create(
            prescription=prescription,
            patient=prescription.patient,
            dispensed_by=request.user,
            status=Dispensation.Status.COMPLETED,
            dispensed_at=timezone.now(),
            notes=request.POST.get('notes', '')
        )

        total_amount = 0
        for item in prescription.items.all():
            # Find matching medication in database
            med = Medication.objects.filter(
                Q(name__icontains=item.medication_name) | Q(dci__icontains=item.medication_name)
            ).first()

            unit_price = med.unit_price if med else 1000
            allocated_batch = None

            if med:
                # FEFO: get oldest unexpired batch with available stock
                batch = med.batches.filter(expiration_date__gt=today, quantity__gt=0).order_by('expiration_date').first()
                if batch:
                    allocated_batch = batch
                    deduct = min(batch.quantity, item.quantity)
                    batch.quantity -= deduct
                    batch.save()

            subtotal = unit_price * item.quantity
            total_amount += subtotal

            DispensationItem.objects.create(
                dispensation=dispensation,
                medication=med if med else Medication.objects.first(),
                batch=allocated_batch,
                quantity=item.quantity,
                unit_price=unit_price,
                subtotal=subtotal
            )

        dispensation.total_amount = total_amount
        dispensation.save()

        prescription.is_dispensed = True
        prescription.dispensed_at = timezone.now()
        prescription.save()

        messages.success(request, _("Ordonnance %(code)s délivrée avec succès. Montant total: %(amt)s FCFA") % {
            'code': prescription.code,
            'amt': f"{total_amount:,.0f}".replace(",", " ")
        })
        return redirect('pharmacy:pending_prescriptions')
