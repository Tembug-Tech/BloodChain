from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
    """Model for user notifications"""
    NOTIFICATION_TYPE_CHOICES = [
        ('emergency_alert', 'Emergency Alert'),
        ('donation_reminder', 'Donation Reminder'),
        ('request_fulfilled', 'Request Fulfilled'),
        ('donation_request', 'Donation Request'),
        ('donation_scheduled', 'Donation Scheduled'),
        ('blood_available', 'Blood Available'),
        ('blood_needed', 'Blood Needed'),
        ('transfer_update', 'Transfer Update'),
        ('reward', 'Reward'),
        ('system', 'System'),
    ]
    
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('read', 'Read'),
        ('failed', 'Failed'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    message = models.TextField()
    blood_type = models.CharField(max_length=3, blank=True, null=True, help_text='Blood type for emergency alerts')
    location = models.CharField(max_length=255, blank=True, null=True, help_text='Location for emergency alerts')
    is_read = models.BooleanField(default=False)
    title = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    read_at = models.DateTimeField(null=True, blank=True)
    related_object_id = models.IntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.recipient.username} - {self.notification_type} - {self.created_at}"


class NotificationPreference(models.Model):
    """Model for user notification preferences"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preference')
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=True)
    donation_requests = models.BooleanField(default=True)
    blood_availability = models.BooleanField(default=True)
    transfer_updates = models.BooleanField(default=True)
    reward_notifications = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Notification Preference - {self.user.username}"
