from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _
from .models import VitalSigns, Consultation, Prescription, PrescriptionItem

class VitalSignsForm(forms.ModelForm):
    class Meta:
        model = VitalSigns
        fields = [
            'patient', 'temperature', 'blood_pressure_systolic', 'blood_pressure_diastolic',
            'pulse_rate', 'respiratory_rate', 'oxygen_saturation', 'weight', 'height', 'notes'
        ]
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'temperature': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.1', 'placeholder': '37.0'}),
            'blood_pressure_systolic': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '120'}),
            'blood_pressure_diastolic': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '80'}),
            'pulse_rate': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '72'}),
            'respiratory_rate': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '16'}),
            'oxygen_saturation': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.1', 'placeholder': '98'}),
            'weight': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.1', 'placeholder': '70.0'}),
            'height': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.5', 'placeholder': '175'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
        }


class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ['symptoms', 'physical_examination', 'diagnosis', 'clinical_notes', 'vital_signs']
        widgets = {
            'vital_signs': forms.Select(attrs={'class': 'form-select'}),
            'symptoms': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': _('Plaintes principales exprimées par le patient...')}),
            'physical_examination': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': _('Constats auscultatoires, palpation...')}),
            'diagnosis': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': _('Diagnostic retenu ou hypothèses différentielles...')}),
            'clinical_notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': _('Plan de traitement, examens prescrits...')}),
        }


class PrescriptionItemForm(forms.ModelForm):
    class Meta:
        model = PrescriptionItem
        fields = ['medication_name', 'dosage', 'duration', 'quantity', 'instructions']
        widgets = {
            'medication_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Amoxicilline 1g'}),
            'dosage': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '1 comprimé matin et soir'}),
            'duration': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '7 jours'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-input', 'min': '1'}),
            'instructions': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Après les repas'}),
        }

PrescriptionItemFormSet = inlineformset_factory(
    Prescription,
    PrescriptionItem,
    form=PrescriptionItemForm,
    extra=2,
    can_delete=True
)
