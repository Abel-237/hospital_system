from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import User

class StaffLoginForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Nom d'utilisateur ou Email"),
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition',
            'placeholder': 'dr.kamga'
        })
    )
    password = forms.CharField(
        label=_("Mot de passe"),
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition',
            'placeholder': '••••••••••••'
        })
    )


class StaffUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'speciality', 'license_number')
        widgets = {
            'role': forms.Select(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-white'}),
            'username': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-white'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-white'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-white'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-white'}),
            'phone_number': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-white', 'placeholder': '+237 670 00 00 00'}),
            'speciality': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-white'}),
            'license_number': forms.TextInput(attrs={'class': 'w-full px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-white'}),
        }


class TwoFactorVerifyForm(forms.Form):
    token = forms.CharField(
        label=_("Code de sécurité (TOTP 6 chiffres)"),
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'w-full text-center tracking-widest text-2xl font-mono px-4 py-3 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:outline-none',
            'placeholder': '123456',
            'autocomplete': 'one-time-code',
            'autofocus': 'autofocus'
        })
    )


class UserProfileForm(forms.ModelForm):
    remove_avatar = forms.BooleanField(
        required=False,
        label=_("Supprimer la photo actuelle"),
        widget=forms.CheckboxInput(attrs={
            'class': 'rounded border-slate-300 dark:border-slate-600 text-red-600 focus:ring-red-500 mr-2'
        })
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'speciality', 'license_number', 'avatar')
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2.5 text-sm text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition',
                'placeholder': _('Ex: Paul')
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2.5 text-sm text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition',
                'placeholder': _('Ex: Kamga')
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2.5 text-sm text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition',
                'placeholder': 'dr.kamga@hospital-cmr.local'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2.5 text-sm text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition',
                'placeholder': '+237 670 00 00 00'
            }),
            'speciality': forms.TextInput(attrs={
                'class': 'form-input w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2.5 text-sm text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition',
                'placeholder': _('Ex: Cardiologie, Urgences, Pédiatrie')
            }),
            'license_number': forms.TextInput(attrs={
                'class': 'form-input w-full rounded-xl border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2.5 text-sm text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:outline-none transition',
                'placeholder': _('Ex: ONMC-2026-XXXX')
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/png, image/jpeg, image/webp, image/gif',
                'id': 'avatar-file-input',
            }),
        }

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # Check maximum file size (2 MB)
            if hasattr(avatar, 'size') and avatar.size > 2 * 1024 * 1024:
                raise forms.ValidationError(_("Le fichier est trop volumineux (maximum 2 Mo)."))
            # Validate extension
            valid_exts = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
            ext = '.' + avatar.name.split('.')[-1].lower() if '.' in avatar.name else ''
            if ext not in valid_exts:
                raise forms.ValidationError(_("Format d'image non supporté. Utilisez PNG, JPG ou WebP."))
        return avatar

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data.get('remove_avatar'):
            if user.avatar:
                user.avatar.delete(save=False)
            user.avatar = None
        if commit:
            user.save()
        return user
