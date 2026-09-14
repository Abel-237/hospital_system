import csv
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Sum
from apps.core.permissions import RoleRequiredMixin
from apps.patients.models import Patient
from apps.consultations.models import Consultation
from .models import Invoice, InvoiceItem, Payment, InsurancePolicy
from .forms import PaymentForm, InsurancePolicyForm
from .services import OrangeMoneyService, MTNMoMoService

class InvoiceListView(RoleRequiredMixin, ListView):
    model = Invoice
    template_name = 'billing/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 20
    allowed_roles = ['CASHIER', 'ADMIN']

    def get_queryset(self):
        qs = Invoice.objects.select_related('patient', 'insurance_policy').all()
        status = self.request.GET.get('status', '')
        q = self.request.GET.get('q', '').strip()

        if status:
            qs = qs.filter(status=status)
        if q:
            qs = qs.filter(
                Q(invoice_number__icontains=q) |
                Q(patient__matricule__icontains=q) |
                Q(patient__first_name__icontains=q) |
                Q(patient__last_name__icontains=q)
            )
        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected_status'] = self.request.GET.get('status', '')
        context['statuses'] = Invoice.Status.choices
        context['q'] = self.request.GET.get('q', '')
        
        # Daily revenue summary
        today = timezone.now().date()
        today_payments = Payment.objects.filter(created_at__date=today, status=Payment.Status.SUCCESS)
        context['today_cash'] = today_payments.filter(method=Payment.Method.CASH).aggregate(s=Sum('amount'))['s'] or 0
        context['today_orange'] = today_payments.filter(method=Payment.Method.ORANGE_MONEY).aggregate(s=Sum('amount'))['s'] or 0
        context['today_mtn'] = today_payments.filter(method=Payment.Method.MTN_MOMO).aggregate(s=Sum('amount'))['s'] or 0
        context['today_total'] = today_payments.aggregate(s=Sum('amount'))['s'] or 0
        return context


class InvoiceDetailView(RoleRequiredMixin, DetailView):
    model = Invoice
    template_name = 'billing/invoice_detail.html'
    context_object_name = 'invoice'
    allowed_roles = ['CASHIER', 'ADMIN', 'DOCTOR']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        invoice = self.object
        context['items'] = invoice.items.all()
        context['payments'] = invoice.payments.select_related('received_by').all().order_by('-created_at')
        context['payment_form'] = PaymentForm(initial={'amount': invoice.remaining_balance})
        return context


class InvoiceAutoGenerateView(RoleRequiredMixin, View):
    """
    Auto-consolidates medical acts for a patient: consultation fees, lab orders, pharmacy dispensations.
    """
    allowed_roles = ['CASHIER', 'ADMIN']

    def get(self, request, patient_id):
        patient = get_object_or_404(Patient, pk=patient_id)
        # Find active insurance
        insurance = patient.insurance_policies.filter(is_active=True).first()
        
        invoice = Invoice.objects.create(
            patient=patient,
            insurance_policy=insurance,
            status=Invoice.Status.PENDING
        )

        # 1. Base Consultation fee (standard rate 5 000 FCFA)
        InvoiceItem.objects.create(
            invoice=invoice,
            description=_("Consultation de médecine générale / spécialiste"),
            category=InvoiceItem.Category.CONSULTATION,
            quantity=1,
            unit_price=Decimal('5000.00')
        )

        # 2. Check pending lab tests for patient today
        today = timezone.now().date()
        for lab in patient.lab_orders.filter(created_at__date=today):
            for item in lab.items.all():
                InvoiceItem.objects.create(
                    invoice=invoice,
                    description=f"{item.test_type.name} [{item.test_type.code}]",
                    category=InvoiceItem.Category.LABORATORY,
                    quantity=1,
                    unit_price=item.test_type.price
                )

        # 3. Check pending pharmacy dispensations today
        for disp in patient.dispensations.filter(created_at__date=today):
            for d_item in disp.items.all():
                InvoiceItem.objects.create(
                    invoice=invoice,
                    description=f"{d_item.medication.name} {d_item.medication.dosage}",
                    category=InvoiceItem.Category.PHARMACY,
                    quantity=d_item.quantity,
                    unit_price=d_item.unit_price
                )

        invoice.recalculate_totals()
        messages.success(request, _("Facture consolidée n°%(num)s générée avec succès.") % {'num': invoice.invoice_number})
        return redirect('billing:invoice_detail', pk=invoice.pk)


class ProcessPaymentView(RoleRequiredMixin, View):
    """
    Process payment transaction for an invoice:
    Supports Cash, Card, Orange Money, and MTN Mobile Money with Push USSD prompt.
    """
    allowed_roles = ['CASHIER', 'ADMIN']

    def post(self, request, invoice_id):
        invoice = get_object_or_404(Invoice, pk=invoice_id)
        form = PaymentForm(request.POST)

        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.received_by = request.user

            method = payment.method
            amount = payment.amount
            phone = payment.payer_phone or invoice.patient.phone

            if method == Payment.Method.CASH or method == Payment.Method.BANK_CARD or method == Payment.Method.INSURANCE_CHECK:
                payment.status = Payment.Status.SUCCESS
                payment.save()
                invoice.paid_amount += amount
                invoice.recalculate_totals()
                messages.success(request, _("Encaissement enregistré avec succès: %(amount)s FCFA") % {
                    'amount': f"{amount:,.0f}".replace(",", " ")
                })

            elif method == Payment.Method.ORANGE_MONEY:
                om = OrangeMoneyService()
                resp = om.request_payment(
                    amount=int(amount),
                    phone=phone,
                    order_id=invoice.invoice_number,
                    reference=payment.payment_reference
                )
                if resp.get('status') == 'SUCCESS':
                    payment.status = Payment.Status.SUCCESS if resp.get('is_mock') else Payment.Status.PENDING_USSD
                    payment.operator_transaction_id = resp.get('txnid', '')
                    payment.gateway_payload = resp
                    payment.save()
                    invoice.paid_amount += amount
                    invoice.recalculate_totals()
                    messages.success(request, _("Paiement Orange Money Cameroun validé pour le numéro %(phone)s (Réf: %(ref)s)") % {
                        'phone': phone,
                        'ref': payment.payment_reference
                    })
                else:
                    payment.status = Payment.Status.FAILED
                    payment.gateway_payload = resp
                    payment.save()
                    messages.error(request, _("Échec de la transaction Orange Money: %(err)s") % {'err': resp.get('error', 'Erreur réseau')})

            elif method == Payment.Method.MTN_MOMO:
                momo = MTNMoMoService()
                resp = momo.request_to_pay(
                    amount=int(amount),
                    phone=phone,
                    external_id=payment.payment_reference,
                    payer_message=f"Reglement Facture {invoice.invoice_number}"
                )
                if resp.get('status') == 'SUCCESS':
                    payment.status = Payment.Status.SUCCESS if resp.get('is_mock') else Payment.Status.PENDING_USSD
                    payment.operator_transaction_id = resp.get('reference_id', '')
                    payment.gateway_payload = resp
                    payment.save()
                    invoice.paid_amount += amount
                    invoice.recalculate_totals()
                    messages.success(request, _("Paiement MTN MoMo Cameroun validé pour le numéro %(phone)s (Réf: %(ref)s)") % {
                        'phone': phone,
                        'ref': payment.payment_reference
                    })
                else:
                    payment.status = Payment.Status.FAILED
                    payment.gateway_payload = resp
                    payment.save()
                    messages.error(request, _("Échec de la requête MTN MoMo: %(err)s") % {'err': resp.get('error', 'Erreur réseau')})

            return redirect('billing:invoice_detail', pk=invoice.pk)
        return redirect('billing:invoice_detail', pk=invoice.pk)


class InvoiceReceiptPDFView(LoginRequiredMixin, View):
    """
    Generate official hospital receipt PDF using WeasyPrint with QR payment verification.
    """
    def get(self, request, pk):
        invoice = get_object_or_404(
            Invoice.objects.select_related('patient', 'insurance_policy').prefetch_related('items', 'payments'),
            pk=pk
        )
        html_string = render_to_string('pdf/invoice_receipt.html', {
            'invoice': invoice,
            'patient': invoice.patient,
            'items': invoice.items.all(),
            'payments': invoice.payments.filter(status=Payment.Status.SUCCESS),
        }, request=request)

        try:
            import weasyprint
            pdf_file = weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri('/')).write_pdf()
            response = HttpResponse(pdf_file, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="Recu_{invoice.invoice_number}.pdf"'
            return response
        except Exception:
            return HttpResponse(html_string)


class AccountingExportCSVView(RoleRequiredMixin, View):
    """
    Export accounting journal (payments, invoices, insurance co-pays) to standard CSV.
    """
    allowed_roles = ['CASHIER', 'ADMIN']

    def get(self, request):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="Journal_Caisse_{timezone.now().strftime("%Y%m%d")}.csv"'
        response.write('\ufeff') # UTF-8 BOM for Excel

        writer = csv.writer(response, delimiter=';')
        writer.writerow([
            'Date/Heure', 'Ref Paiement', 'No Facture', 'Matricule Patient',
            'Nom Patient', 'Mode Reglement', 'Montant (FCFA)', 'Statut', 'Caissier'
        ])

        payments = Payment.objects.select_related('invoice__patient', 'received_by').all().order_by('-created_at')
        for p in payments:
            writer.writerow([
                p.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                p.payment_reference,
                p.invoice.invoice_number,
                p.invoice.patient.matricule,
                p.invoice.patient.full_name,
                p.get_method_display(),
                f"{p.amount:.2f}",
                p.get_status_display(),
                p.received_by.full_name if p.received_by else ''
            ])

        return response
