"""
Orange Money Cameroon Payment Integration Service.
Compliant with Orange Money Web Payment and OM API specs.
"""
import uuid
import logging
import requests
from django.conf import settings
from apps.core.utils import clean_cameroon_phone

logger = logging.getLogger(__name__)

class OrangeMoneyService:
    def __init__(self):
        om_config = getattr(settings, 'ORANGE_MONEY', {})
        self.env = om_config.get('ENV', 'sandbox')
        self.client_id = om_config.get('CLIENT_ID', '')
        self.client_secret = om_config.get('CLIENT_SECRET', '')
        self.merchant_key = om_config.get('MERCHANT_KEY', '')
        self.notification_url = om_config.get('NOTIFICATION_URL', '')
        self.currency = om_config.get('CURRENCY', 'XAF')

        # Orange Money API URLs
        if self.env == 'production':
            self.base_url = "https://api.orange.com/orange-money-webpay/cm/v1"
            self.token_url = "https://api.orange.com/oauth/v3/token"
        else:
            self.base_url = "https://api.orange.com/orange-money-webpay/dev/v1"
            self.token_url = "https://api.orange.com/oauth/v3/token"

    def is_configured(self) -> bool:
        """Return True only when non-placeholder credentials are present."""
        def _valid(value: str) -> bool:
            return bool(value) and not value.startswith('your_')
        return _valid(self.client_id) and _valid(self.client_secret) and _valid(self.merchant_key)

    def request_payment(self, amount: int, phone: str, order_id: str, reference: str) -> dict:
        """
        Initiates a payment request to Orange Money Cameroon.
        Sends a USSD push prompt directly to the patient's phone (+237 69X XX XX XX).
        """
        formatted_phone = clean_cameroon_phone(phone).replace('+', '')
        
        # Development / Sandbox mock mode when real credentials are not yet entered
        if not self.is_configured():
            logger.info(f"[ORANGE_MONEY_MOCK] Simulating payment request for {amount} XAF from {formatted_phone}")
            simulated_tx_id = f"OM-CMR-{uuid.uuid4().hex[:10].upper()}"
            return {
                'status': 'SUCCESS',
                'payment_url': f"https://mock-orange.cm/pay/{simulated_tx_id}",
                'notif_token': simulated_tx_id,
                'txnid': simulated_tx_id,
                'message': 'Simulated USSD push sent to phone #150*50#',
                'is_mock': True
            }

        try:
            # 1. Fetch OAuth2 Bearer Token
            token_resp = requests.post(
                self.token_url,
                headers={'Authorization': f'Basic {self._get_basic_auth()}'},
                data={'grant_type': 'client_credentials'},
                timeout=10
            )
            token_resp.raise_for_status()
            access_token = token_resp.json().get('access_token')

            # 2. Initiate WebPay transaction
            payload = {
                "merchant_key": self.merchant_key,
                "currency": self.currency,
                "order_id": order_id,
                "amount": int(amount),
                "return_url": self.notification_url,
                "cancel_url": self.notification_url,
                "notif_url": self.notification_url,
                "lang": "fr",
                "reference": reference,
            }

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            resp = requests.post(f"{self.base_url}/webpayment", json=payload, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            return {
                'status': 'SUCCESS',
                'payment_url': data.get('payment_url'),
                'notif_token': data.get('notif_token'),
                'txnid': data.get('txnid'),
                'is_mock': False
            }

        except Exception as e:
            logger.error(f"Orange Money API error: {str(e)}")
            return {
                'status': 'FAILED',
                'error': str(e),
                'is_mock': False
            }

    def _get_basic_auth(self) -> str:
        import base64
        credentials = f"{self.client_id}:{self.client_secret}"
        return base64.b64encode(credentials.encode()).decode()
