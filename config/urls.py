"""
URL configuration for Hospital Management System.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from apps.core.views import RootRedirectView, HealthCheckView, custom_set_language

urlpatterns = [
    # Language switch endpoint (custom handler resolves between prefixed and default URLs)
    path('i18n/setlang/', custom_set_language, name='set_language'),
    path('i18n/', include('django.conf.urls.i18n')),
    path('health/', HealthCheckView.as_view(), name='health_check'),
    
    # API endpoints (not language-prefixed)
    path('api/v1/', include('apps.api.urls')),
    
    # Webhook endpoints for Mobile Money (cannot have language prefixes)
    path('billing/webhook/', include('apps.billing.webhook_urls')),
]

# Localized URL patterns for Web UI
urlpatterns += i18n_patterns(
    path('', RootRedirectView.as_view(), name='root_redirect'),
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('dashboard/', include('apps.core.urls')),
    path('patients/', include('apps.patients.urls')),
    path('appointments/', include('apps.appointments.urls')),
    path('consultations/', include('apps.consultations.urls')),
    path('pharmacy/', include('apps.pharmacy.urls')),
    path('laboratory/', include('apps.laboratory.urls')),
    path('rooms/', include('apps.rooms.urls')),
    path('billing/', include('apps.billing.urls')),
    path('notifications/', include('apps.notifications.urls')),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
