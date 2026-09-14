from django.conf import settings

def hospital_context(request):
    """
    Context processor to inject hospital metadata and user permissions helper into all templates.
    """
    profile = getattr(settings, 'HOSPITAL_PROFILE', {
        'NAME': 'Centre Hospitalier Universitaire Régional',
        'NAME_EN': 'Regional University Teaching Hospital',
        'PHONE': '+237 670 000 000',
        'EMAIL': 'contact@hospital-cmr.local',
        'ADDRESS': 'Douala / Yaoundé, Cameroun',
        'CURRENCY': 'FCFA',
    })
    
    profile_data = dict(profile)
    current_lang = getattr(request, 'LANGUAGE_CODE', 'fr')
    if current_lang == 'en' and 'NAME_EN' in profile_data:
        profile_data['NAME'] = profile_data['NAME_EN']
    
    user_role = getattr(request.user, 'role', None) if request.user.is_authenticated else None
    
    return {
        'HOSPITAL': profile_data,
        'CURRENT_USER_ROLE': user_role,
        'IS_DOCTOR': user_role == 'DOCTOR',
        'IS_NURSE': user_role == 'NURSE',
        'IS_ADMIN': user_role == 'ADMIN' or getattr(request.user, 'is_superuser', False),
        'IS_PHARMACIST': user_role == 'PHARMACIST',
        'IS_LABORANT': user_role == 'LABORANT',
        'IS_CASHIER': user_role == 'CASHIER',
        'IS_RECEPTIONIST': user_role == 'RECEPTIONIST',
    }
