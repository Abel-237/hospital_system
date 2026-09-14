from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
import json
import logging
from .models import Payment

logger = logging.getLogger(__name__)

@csrf_exempt
def orange_money_webhook(request):
    """
    Handle Orange Money Cameroon IPN / Webhook callback.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            txnid = data.get('txnid')
            status = data.get('status')
            
            logger.info(f"Orange Money Webhook received: order={order_id}, txn={txnid}, status={status}")
            
            if status == 'SUCCESS':
                payment = Payment.objects.filter(operator_transaction_id=txnid).first()
                if payment and payment.status != Payment.Status.SUCCESS:
                    payment.status = Payment.Status.SUCCESS
                    payment.gateway_payload = data
                    payment.save()
                    payment.invoice.paid_amount += payment.amount
                    payment.invoice.recalculate_totals()
            return HttpResponse("OK", status=200)
        except Exception as e:
            logger.error(f"Error handling Orange Money webhook: {e}")
            return HttpResponse("Bad Request", status=400)
    return HttpResponse("Method not allowed", status=405)


@csrf_exempt
def mtn_momo_webhook(request):
    """
    Handle MTN Mobile Money Cameroon callback.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            financial_txn_id = data.get('financialTransactionId')
            external_id = data.get('externalId')
            status = data.get('status')

            logger.info(f"MTN MoMo Webhook received: ext={external_id}, txn={financial_txn_id}, status={status}")

            if status == 'SUCCESSFUL':
                payment = Payment.objects.filter(payment_reference=external_id).first()
                if payment and payment.status != Payment.Status.SUCCESS:
                    payment.status = Payment.Status.SUCCESS
                    payment.operator_transaction_id = financial_txn_id or ''
                    payment.gateway_payload = data
                    payment.save()
                    payment.invoice.paid_amount += payment.amount
                    payment.invoice.recalculate_totals()
            return HttpResponse("OK", status=200)
        except Exception as e:
            logger.error(f"Error handling MTN MoMo webhook: {e}")
            return HttpResponse("Bad Request", status=400)
    return HttpResponse("Method not allowed", status=405)


urlpatterns = [
    path('orange-money/', orange_money_webhook, name='orange_money_webhook'),
    path('mtn-momo/', mtn_momo_webhook, name='mtn_momo_webhook'),
]
