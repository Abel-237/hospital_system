from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Admission, NursingNote, Bed

class AdmissionForm(forms.ModelForm):
    class Meta:
        model = Admission
        fields = ['patient', 'bed', 'admission_reason']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select w-full'}),
            'bed': forms.Select(attrs={'class': 'form-select w-full'}),
            'admission_reason': forms.Textarea(attrs={'class': 'form-textarea w-full', 'rows': 3, 'placeholder': _('Motif d’admission, diagnostic initial...')}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show available beds (or the current bed if editing)
        queryset = Bed.objects.filter(status=Bed.Status.AVAILABLE).select_related('room__ward')
        if self.instance and self.instance.pk and self.instance.bed_id:
            queryset = (queryset | Bed.objects.filter(pk=self.instance.bed_id)).distinct()
        self.fields['bed'].queryset = queryset
        self.fields['bed'].label_from_instance = lambda obj: (
            f"[{obj.room.ward.code}] {obj.room.ward.name} — Ch. {obj.room.room_number} ({obj.room.get_room_type_display()}) — Lit {obj.bed_number} ({int(obj.room.daily_rate):,} FCFA/j)".replace(',', ' ')
        )
        self.fields['bed'].empty_label = _("- Choisir un lit disponible -")
        self.fields['patient'].empty_label = _("- Choisir un patient -")


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
