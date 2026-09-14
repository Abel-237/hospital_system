from django.urls import path
from .views import (
    StaffLoginView, StaffLogoutView, TwoFactorVerifyView,
    TwoFactorSetupView, StaffProfileView, StaffListView, StaffCreateView
)

app_name = 'accounts'

urlpatterns = [
    path('login/', StaffLoginView.as_view(), name='login'),
    path('logout/', StaffLogoutView.as_view(), name='logout'),
    path('2fa/verify/', TwoFactorVerifyView.as_view(), name='2fa_verify'),
    path('2fa/setup/', TwoFactorSetupView.as_view(), name='2fa_setup'),
    path('profile/', StaffProfileView.as_view(), name='profile'),
    path('staff/', StaffListView.as_view(), name='staff_list'),
    path('staff/create/', StaffCreateView.as_view(), name='staff_create'),
]
