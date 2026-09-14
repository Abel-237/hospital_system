from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.permissions import RoleRequiredMixin
from .models import NotificationLog

class NotificationLogListView(RoleRequiredMixin, ListView):
    model = NotificationLog
    template_name = 'notifications/log_list.html'
    context_object_name = 'logs'
    paginate_by = 25
    allowed_roles = ['ADMIN']
