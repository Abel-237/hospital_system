"""
Cameroon SMS Gateway Client & Abstraction.
Supports integration with local providers (e.g. Orange SMS API, MTN SMS, or local aggregators).
"""
import logging
import requests
from django.conf import settings
from apps.core.utils import clean_cameroon_phone

logger = logging.getLogger(__name__)

class CameroonSMSService:
    def __init__(self):
        config = getattr(settings, 'SMS_GATEWAY', {})
        self.url = config.get('URL', '')
        self.api_key = config.get('API_KEY', '')
        self.sender_id = config.get('SENDER_ID', 'HOSP_CMR')

    def send_sms(self, to_phone: str, message_text: str) -> dict:
        """
        Send SMS to Cameroon phone (+237 6XX XX XX XX).
        Falls back to local logging when API_KEY is empty in development.
        """
        phone = clean_cameroon_phone(to_phone)
        if not self.api_key:
            logger.info(f"[DEV_SMS_GATEWAY] To: {phone} | Sender: {self.sender_id} | Msg: {message_text}")
            return {
                'success': True,
                'message_id': f"DEV-SMS-{phone}",
                'is_mock': True
            }

        try:
            payload = {
                'sender': self.sender_id,
                'recipient': phone,
                'message': message_text
            }
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            resp = requests.post(self.url, json=payload, headers=headers, timeout=10)
            resp.raise_for_status()
            return {
                'success': True,
                'data': resp.json(),
                'is_mock': False
            }
        except Exception as e:
            logger.error(f"SMS Gateway dispatch failed to {phone}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'is_mock': False
            }
