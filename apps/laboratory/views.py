from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.core.permissions import RoleRequiredMixin
from apps.patients.models import Patient
from .models import LabOrder, LabOrderItem, LabTestType
from .forms import LabOrderCreateForm, LabResultEntryForm

class LabOrderListView(LoginRequiredMixin, ListView):
    model = LabOrder
    template_name = 'laboratory/lab_order_list.html'
    context_object_name = 'orders'
    paginate_by = 20

    def get_queryset(self):
        qs = LabOrder.objects.select_related('patient', 'prescribed_by').prefetch_related('items__test_type')
        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_status'] = self.request.GET.get('status', '')
        context['statuses'] = LabOrder.Status.choices
        return context


class LabOrderCreateView(RoleRequiredMixin, View):
    allowed_roles = ['DOCTOR', 'ADMIN']

    def get(self, request):
        initial = {}
        patient_id = request.GET.get('patient')
        if patient_id:
            initial['patient'] = get_object_or_404(Patient, pk=patient_id)
        form = LabOrderCreateForm(initial=initial)
        return render(request, 'laboratory/lab_order_form.html', {'form': form})

    def post(self, request):
        form = LabOrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.prescribed_by = request.user
            order.save()
            for test in form.cleaned_data['tests']:
                LabOrderItem.objects.create(order=order, test_type=test)
            messages.success(request, _("Bon d’analyses n°%(order)s prescrit pour %(patient)s.") % {
                'order': order.order_number,
                'patient': order.patient.full_name
            })
            return redirect('laboratory:order_detail', pk=order.pk)
        return render(request, 'laboratory/lab_order_form.html', {'form': form})


class LabOrderDetailView(LoginRequiredMixin, DetailView):
    model = LabOrder
    template_name = 'laboratory/lab_order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items'] = self.object.items.select_related('test_type', 'analyzed_by').all()
        return context


class LabResultUpdateView(RoleRequiredMixin, View):
    allowed_roles = ['LABORANT', 'ADMIN']

    def get(self, request, item_id):
        item = get_object_or_404(LabOrderItem.objects.select_related('test_type', 'order__patient'), pk=item_id)
        form = LabResultEntryForm(instance=item)
        return render(request, 'laboratory/lab_result_entry.html', {'item': item, 'form': form})

    def post(self, request, item_id):
        item = get_object_or_404(LabOrderItem, pk=item_id)
        form = LabResultEntryForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            result = form.save(commit=False)
            result.analyzed_by = request.user
            result.analyzed_at = timezone.now()
            result.save()

            # Check if all items in order are analyzed
            order = item.order
            all_filled = not order.items.filter(result_value='').exists()
            if all_filled:
                order.status = LabOrder.Status.COMPLETED
                order.completed_at = timezone.now()
                order.save()
            else:
                order.status = LabOrder.Status.IN_PROGRESS
                order.save()

            messages.success(request, _("Résultat pour %(test)s enregistré avec succès.") % {'test': item.test_type.name})
            return redirect('laboratory:order_detail', pk=order.pk)
        return render(request, 'laboratory/lab_result_entry.html', {'item': item, 'form': form})


class LabReportPDFView(LoginRequiredMixin, View):
    """
    Generate official PDF laboratory report using WeasyPrint with normal ranges.
    """
    def get(self, request, pk):
        order = get_object_or_404(
            LabOrder.objects.select_related('patient', 'prescribed_by').prefetch_related('items__test_type', 'items__analyzed_by'),
            pk=pk
        )
        html_string = render_to_string('pdf/lab_report.html', {
            'order': order,
            'patient': order.patient,
            'doctor': order.prescribed_by,
            'items': order.items.all(),
        }, request=request)

        try:
            import weasyprint
            pdf_file = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="Rapport_Labo_{order.order_number}.pdf"'
            return response
        except Exception:
            return HttpResponse(html_string)
