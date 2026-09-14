from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Admission, NursingNote, Bed

class AdmissionForm(forms.ModelForm):
    class Meta:
        model = Admission
        fields = ['patient', 'bed', 'admission_reason']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'bed': forms.Select(attrs={'class': 'form-select'}),
            'admission_reason': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': _('Motif d’admission, diagnostic initial...')}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show available beds
        self.fields['bed'].queryset = Bed.objects.filter(status=Bed.Status.AVAILABLE).select_related('room__ward')


class DischargeForm(forms.ModelForm):
    class Meta:
        model = Admission
        fields = ['discharge_summary']
        widgets = {
            'discharge_summary': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4, 'placeholder': _('Résumé de l’évolution clinique, traitement de sortie et consignes de suivi...')}),
        }


class NursingNoteForm(forms.ModelForm):
    class Meta:
        model = NursingNote
        fields = ['observation', 'administered_treatments']
        widgets = {
            'observation': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3, 'placeholder': _('État du patient, réactivité, douleur, constantes...')}),
            'administered_treatments': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': _('Médicaments injectés, pansements refaits...')}),
        }
