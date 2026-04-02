from django.contrib import admin
from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'notification_type', 'title', 'status', 'created_at']
    list_filter = ['notification_type', 'status', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Notification Information', {
            'fields': ('user', 'notification_type', 'title', 'message', 'status')
        }),
        ('Related Object', {
            'fields': ('related_object_id', 'related_object_type'),
            'classes': ('collapse',)
        }),
        ('Read Information', {
            'fields': ('read_at',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_notifications', 'sms_notifications', 'push_notifications']
    list_filter = ['email_notifications', 'sms_notifications', 'push_notifications']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']
