from django.contrib import admin
from .models import NotificationLog

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'channel', 'subject', 'status', 'sent_at', 'created_at')
    list_filter = ('channel', 'status', 'created_at')
    search_fields = ('recipient', 'subject', 'message')
    readonly_fields = ('created_at', 'updated_at')
