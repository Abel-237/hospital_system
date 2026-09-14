import pytest
from decimal import Decimal
from django.urls import reverse
from apps.billing.models import Invoice, InvoiceItem, Payment, InsurancePolicy
from apps.billing.services import OrangeMoneyService, MTNMoMoService

@pytest.mark.django_db
def test_invoice_insurance_calculation(patient_record):
    insurance = InsurancePolicy.objects.create(
        patient=patient_record,
        company_name='Ascoma Assurances',
        policy_number='POL-12345',
        coverage_percentage=Decimal('80.00'),
        is_active=True
    )

    invoice = Invoice.objects.create(
        patient=patient_record,
        insurance_policy=insurance
    )

    InvoiceItem.objects.create(
        invoice=invoice,
        description='Consultation Spécialiste',
        category=InvoiceItem.Category.CONSULTATION,
        quantity=1,
        unit_price=Decimal('10000.00')
    )

    invoice.recalculate_totals()

    assert invoice.total_gross == Decimal('10000.00')
    assert invoice.insurance_amount == Decimal('8000.00')
    assert invoice.patient_net_amount == Decimal('2000.00')
    assert invoice.remaining_balance == Decimal('2000.00')

@pytest.mark.django_db
def test_mobile_money_simulation(client, cashier_user, patient_record):
    client.force_login(cashier_user)

    invoice = Invoice.objects.create(
        patient=patient_record,
        total_gross=Decimal('5000.00'),
        patient_net_amount=Decimal('5000.00')
    )

    # 1. Orange Money Mock
    om_svc = OrangeMoneyService()
    om_res = om_svc.request_payment(amount=5000, phone='+237690000000', order_id=invoice.invoice_number, reference='REF-OM-1')
    assert om_res['status'] == 'SUCCESS'
    assert om_res['is_mock'] is True

    # 2. MTN MoMo Mock
    momo_svc = MTNMoMoService()
    momo_res = momo_svc.request_to_pay(amount=5000, phone='+237670000000', external_id='REF-MOMO-1', payer_message='Test')
    assert momo_res['status'] == 'SUCCESS'
    assert momo_res['is_mock'] is True
