from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Medication, StockBatch, Dispensation

class MedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        fields = ['name', 'dci', 'form', 'dosage', 'unit_price', 'critical_stock_threshold', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Paracétamol Biogaran'}),
            'dci': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Paracetamol'}),
            'form': forms.Select(attrs={'class': 'form-select'}),
            'dosage': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: 500mg'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '1500'}),
            'critical_stock_threshold': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '20'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600 rounded'}),
        }


class StockBatchForm(forms.ModelForm):
    class Meta:
        model = StockBatch
        fields = ['medication', 'batch_number', 'expiration_date', 'quantity', 'purchase_price']
        widgets = {
            'medication': forms.Select(attrs={'class': 'form-select'}),
            'batch_number': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'LOT-2026-X'}),
            'expiration_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input', 'min': '1'}),
            'purchase_price': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '1000'}),
        }
