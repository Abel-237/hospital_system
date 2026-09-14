import pytest
from datetime import date, timedelta
from decimal import Decimal
from apps.pharmacy.models import Medication, StockBatch

@pytest.mark.django_db
def test_medication_and_batch_fefo():
    today = date.today()
    med = Medication.objects.create(
        name='Amoxicilline 1g',
        dci='Amoxicillin',
        dosage='1000mg',
        unit_price=Decimal('2500.00'),
        critical_stock_threshold=10
    )

    # Add 2 batches with different expiration dates
    batch1 = StockBatch.objects.create(
        medication=med,
        batch_number='LOT-2026-A',
        expiration_date=today + timedelta(days=90),
        quantity=5
    )
    batch2 = StockBatch.objects.create(
        medication=med,
        batch_number='LOT-2026-B',
        expiration_date=today + timedelta(days=365),
        quantity=20
    )

    assert med.total_stock == 25
    assert med.is_critical_stock is False

    # Simulate stock reduction
    batch1.quantity = 0
    batch1.save()
    batch2.quantity = 4
    batch2.save()

    assert med.total_stock == 4
    assert med.is_critical_stock is True
