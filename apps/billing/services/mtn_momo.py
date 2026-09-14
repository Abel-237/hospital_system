"""
MTN Mobile Money Cameroon Open API Integration Service (Collection).
"""
import uuid
import logging
import requests
from django.conf import settings
from apps.core.utils import clean_cameroon_phone

logger = logging.getLogger(__name__)

class MTNMoMoService:
    def __init__(self):
        momo_config = getattr(settings, 'MTN_MOMO', {})
        self.env = momo_config.get('ENV', 'sandbox')
        self.primary_key = momo_config.get('PRIMARY_KEY', '')
        self.api_user = momo_config.get('API_USER', '')
        self.api_key = momo_config.get('API_KEY', '')
        self.target_env = momo_config.get('TARGET_ENV', 'sandbox')
        self.currency = momo_config.get('CURRENCY', 'XAF')

        if self.env == 'production':
            self.base_url = "https://proxy.momoapi.mtn.com/collection"
        else:
            self.base_url = "https://sandbox.momodeveloper.mtn.com/collection"

    def is_configured(self) -> bool:
        """Return True only when non-placeholder credentials are present."""
        def _valid(value: str) -> bool:
            return bool(value) and not value.startswith('your_')
        return _valid(self.primary_key) and _valid(self.api_user) and _valid(self.api_key)

    def request_to_pay(self, amount: int, phone: str, external_id: str, payer_message: str) -> dict:
        """
        Sends an MTN Mobile Money collection request (requesttopay).
        Triggers an immediate USSD approval popup (*126#) on the user phone.
        """
        formatted_phone = clean_cameroon_phone(phone).replace('+', '')
        
        # Development / Sandbox mock mode when real credentials are not yet entered
        if not self.is_configured():
            logger.info(f"[MTN_MOMO_MOCK] Simulating requesttopay for {amount} XAF from {formatted_phone}")
            reference_id = str(uuid.uuid4())
            return {
                'status': 'SUCCESS',
                'reference_id': reference_id,
                'external_id': external_id,
                'message': 'Simulated MTN MoMo USSD prompt sent to phone (*126#)',
                'is_mock': True
            }

        try:
            # 1. Generate Token
            token_resp = requests.post(
                f"{self.base_url}/token/",
                headers={
                    'Ocp-Apim-Subscription-Key': self.primary_key,
                    'Authorization': f'Basic {self._get_basic_auth()}'
                },
                timeout=10
            )
            token_resp.raise_for_status()
            token = token_resp.json().get('access_token')

            # 2. Request to pay
            reference_id = str(uuid.uuid4())
            payload = {
                "amount": str(int(amount)),
                "currency": self.currency,
                "externalId": external_id,
                "payer": {
                    "partyIdType": "MSISDN",
                    "partyId": formatted_phone
                },
                "payerMessage": payer_message,
                "payeeNote": f"Hospital Invoice {external_id}"
            }

            headers = {
                'Authorization': f'Bearer {token}',
                'X-Reference-Id': reference_id,
                'X-Target-Environment': self.target_env,
                'Ocp-Apim-Subscription-Key': self.primary_key,
                'Content-Type': 'application/json'
            }

            resp = requests.post(f"{self.base_url}/v1_0/requesttopay", json=payload, headers=headers, timeout=15)
            # MTN returns 202 Accepted on successful queueing
            if resp.status_code in [200, 202]:
                return {
                    'status': 'SUCCESS',
                    'reference_id': reference_id,
                    'external_id': external_id,
                    'is_mock': False
                }
            else:
                return {
                    'status': 'FAILED',
                    'error': resp.text,
                    'is_mock': False
                }

        except Exception as e:
            logger.error(f"MTN MoMo API error: {str(e)}")
            return {
                'status': 'FAILED',
                'error': str(e),
                'is_mock': False
            }

    def _get_basic_auth(self) -> str:
        import base64
        credentials = f"{self.api_user}:{self.api_key}"
        return base64.b64encode(credentials.encode()).decode()
