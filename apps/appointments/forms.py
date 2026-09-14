from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Appointment
from apps.accounts.models import User

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            'patient', 'doctor', 'scheduled_date', 'scheduled_time',
            'reason', 'priority', 'notes'
        ]
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'scheduled_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'scheduled_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-input'}),
            'reason': forms.TextInput(attrs={'class': 'form-input', 'placeholder': _('Ex: Consultation générale, suivi tension...')}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].queryset = User.objects.filter(role=User.Role.DOCTOR, is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        scheduled_date = cleaned_data.get('scheduled_date')
        scheduled_time = cleaned_data.get('scheduled_time')

        if doctor and scheduled_date and scheduled_time:
            # Check collision
            collision = Appointment.objects.filter(
                doctor=doctor,
                scheduled_date=scheduled_date,
                scheduled_time=scheduled_time,
            )
            if self.instance.pk:
                collision = collision.exclude(pk=self.instance.pk)
            if collision.exists():
                raise forms.ValidationError(_("Ce médecin a déjà une consultation programmée à cette heure précise. Veuillez choisir un autre créneau."))
        return cleaned_data
