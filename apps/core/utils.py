import re
import uuid
from datetime import datetime
from django.utils import timezone

def generate_matricule(prefix="CMR", year=None):
    """
    Generate unique sequential/timestamp-based patient matricule.
    Example: CMR-2026-9A8B7C
    """
    if year is None:
        year = timezone.now().year
    suffix = uuid.uuid4().hex[:6].upper()
    return f"{prefix}-{year}-{suffix}"


def clean_cameroon_phone(phone: str) -> str:
    """
    Clean and format phone number for Cameroon (+237).
    Accepts: '670000000', '237670000000', '+237 670 00 00 00'.
    Returns standard E.164: '+237670000000'.
    """
    if not phone:
        return ""
    digits = re.sub(r'\D', '', phone)
    if digits.startswith('237') and len(digits) == 12:
        return f"+{digits}"
    elif len(digits) == 9:
        return f"+237{digits}"
    return f"+{digits}" if not phone.startswith('+') else phone


def detect_cameroon_operator(phone: str) -> str:
    """
    Detect Cameroon carrier: MTN, ORANGE, or OTHER.
    MTN prefixes: 67, 68, 650, 651, 652, 653, 654
    Orange prefixes: 69, 655, 656, 657, 658, 659
    """
    cleaned = clean_cameroon_phone(phone)
    if not cleaned.startswith('+237') or len(cleaned) != 13:
        return 'UNKNOWN'
    
    local = cleaned[4:] # 9 digits
    if local.startswith(('67', '68')) or local.startswith(('650', '651', '652', '653', '654')):
        return 'MTN'
    elif local.startswith('69') or local.startswith(('655', '656', '657', '658', '659')):
        return 'ORANGE'
    return 'OTHER'
