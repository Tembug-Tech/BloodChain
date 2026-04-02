from rest_framework import serializers
from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    recipient_name = serializers.CharField(source='recipient.get_full_name', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'recipient_name', 'notification_type', 'message', 
            'blood_type', 'location', 'is_read', 'title', 'status', 'read_at', 
            'related_object_id', 'related_object_type', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'recipient_name']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for NotificationPreference model"""
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'user', 'email_notifications', 'sms_notifications', 'push_notifications',
            'donation_requests', 'blood_availability', 'transfer_updates', 'reward_notifications',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
