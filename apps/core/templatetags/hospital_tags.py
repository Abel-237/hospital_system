from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='currency_fcfa')
def currency_fcfa(value):
    """
    Format numeric value into Cameroon FCFA (XAF).
    Example: 15000 -> 15 000 FCFA
    """
    try:
        val = float(value)
        formatted = f"{val:,.0f}".replace(",", " ")
        return f"{formatted} FCFA"
    except (ValueError, TypeError):
        return f"{value} FCFA"


@register.filter(name='role_badge')
def role_badge(role):
    """
    Return colored Tailwind badge HTML for user role.
    """
    colors = {
        'ADMIN': 'bg-purple-100 text-purple-800 border-purple-300 dark:bg-purple-900/40 dark:text-purple-300',
        'DOCTOR': 'bg-blue-100 text-blue-800 border-blue-300 dark:bg-blue-900/40 dark:text-blue-300',
        'NURSE': 'bg-emerald-100 text-emerald-800 border-emerald-300 dark:bg-emerald-900/40 dark:text-emerald-300',
        'RECEPTIONIST': 'bg-amber-100 text-amber-800 border-amber-300 dark:bg-amber-900/40 dark:text-amber-300',
        'PHARMACIST': 'bg-teal-100 text-teal-800 border-teal-300 dark:bg-teal-900/40 dark:text-teal-300',
        'LABORANT': 'bg-indigo-100 text-indigo-800 border-indigo-300 dark:bg-indigo-900/40 dark:text-indigo-300',
        'CASHIER': 'bg-rose-100 text-rose-800 border-rose-300 dark:bg-rose-900/40 dark:text-rose-300',
    }
    css = colors.get(role, 'bg-gray-100 text-gray-800 border-gray-300 dark:bg-gray-800 dark:text-gray-300')
    return mark_safe(f'<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border {css}">{role}</span>')
