from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from simple_history.admin import SimpleHistoryAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin, SimpleHistoryAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'is_2fa_enabled', 'is_staff')
    list_filter = ('role', 'is_2fa_enabled', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations Professionnelles Hospitalières', {
            'fields': ('role', 'phone_number', 'speciality', 'license_number', 'is_2fa_enabled')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations Professionnelles Hospitalières', {
            'fields': ('role', 'phone_number', 'speciality', 'license_number')
        }),
    )
