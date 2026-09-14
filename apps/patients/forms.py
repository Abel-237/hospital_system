from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import Patient

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'first_name', 'last_name', 'birth_date', 'gender', 'blood_group',
            'phone', 'email', 'address', 'city',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation',
            'allergies', 'chronic_conditions', 'family_history', 'surgical_history',
            'consent_given'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Jean'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Mbarga'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+237 670 00 00 00'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'patient@example.cm'}),
            'address': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Bonanjo, Rue 123'}),
            'city': forms.TextInput(attrs={'class': 'form-input'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-input'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+237 690 00 00 00'}),
            'emergency_contact_relation': forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Époux(se), Parent, Frère...')}),
            'allergies': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': _('Pénicilline, Aspirine, Cacahuètes...')}),
            'chronic_conditions': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': _('Hypertension artérielle, Drépanocytose SS...')}),
            'family_history': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
            'surgical_history': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
            'consent_given': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-blue-600 rounded'}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.consent_given and not instance.consent_given_at:
            instance.consent_given_at = timezone.now()
        if commit:
            instance.save()
        return instance
