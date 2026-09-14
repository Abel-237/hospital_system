from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Invoice, InvoiceItem, Payment, InsurancePolicy

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['method', 'amount', 'payer_phone']
        widgets = {
            'method': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '100'}),
            'payer_phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+237 6XX XX XX XX'}),
        }


class InsurancePolicyForm(forms.ModelForm):
    class Meta:
        model = InsurancePolicy
        fields = ['company_name', 'policy_number', 'coverage_percentage', 'valid_until', 'is_active']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Ascoma / Saham'}),
            'policy_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'POL-987654'}),
            'coverage_percentage': forms.NumberInput(attrs={'class': 'form-input', 'step': '1', 'min': '0', 'max': '100'}),
            'valid_until': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600 rounded'}),
        }
