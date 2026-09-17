from django import forms
from django.utils.translation import gettext_lazy as _
from .models import LabOrder, LabOrderItem, LabTestType

class LabOrderCreateForm(forms.ModelForm):
    tests = forms.ModelMultipleChoiceField(
        queryset=LabTestType.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple(),
        label=_("Examens à prescrire")
    )

    class Meta:
        model = LabOrder
        fields = ['patient', 'priority', 'clinical_indications']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select w-full'}),
            'priority': forms.Select(attrs={'class': 'form-select w-full'}),
            'clinical_indications': forms.Textarea(attrs={'class': 'form-textarea w-full', 'rows': 3, 'placeholder': _('Suspicion paludisme, bilan préopératoire...')}),
        }


class LabResultEntryForm(forms.ModelForm):
    class Meta:
        model = LabOrderItem
        fields = ['result_value', 'is_abnormal', 'technician_notes', 'attachment']
        widgets = {
            'result_value': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: 14.2 g/dL ou Positif (++)'}),
            'is_abnormal': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-red-600 rounded'}),
            'technician_notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2, 'placeholder': _('Présence de trophozoïtes de Plasmodium falciparum...')}),
        }
