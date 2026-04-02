"""
Notification service functions for BloodChain
"""
from django.utils import timezone
from donor.models import Donor
from .models import Notification


def send_emergency_alert(blood_type, location):
    """
    Send emergency alert to all available donors with matching blood type near the location.
    
    Args:
        blood_type (str): Blood type needed (e.g., 'O+', 'A-', etc.)
        location (str): Location where blood is needed
    
    Returns:
        list: List of created Notification objects
    """
    # Find all available donors with matching blood type near the location
    matching_donors = Donor.objects.filter(
        blood_type=blood_type,
        is_available=True,
        location__icontains=location.split(',')[0] if ',' in location else location
    )
    
    created_notifications = []
    
    for donor in matching_donors:
        # Check if donor user exists
        if donor.user:
            message = f"Emergency blood request! {blood_type} blood needed urgently at {location}. Your donation could save a life!"
            
            notification = Notification.objects.create(
                recipient=donor.user,
                notification_type='emergency_alert',
                message=message,
                blood_type=blood_type,
                location=location,
                title=f"Emergency Alert: {blood_type} Blood Needed",
                status='sent',
                is_read=False
            )
            created_notifications.append(notification)
    
    return created_notifications


def send_donation_reminder(donor_user, days_since_donation=35):
    """
    Send donation reminder to a donor.
    
    Args:
        donor_user: Django User object of the donor
        days_since_donation (int): Days since last eligible donation
    
    Returns:
        Notification: Created notification object or None
    """
    try:
        donor = donor_user.donor_profile
        message = f"You're now eligible to donate blood! Your last donation was {days_since_donation} days ago. Please donate soon to help save lives."
        
        notification = Notification.objects.create(
            recipient=donor_user,
            notification_type='donation_reminder',
            message=message,
            blood_type=donor.blood_type,
            location=donor.location,
            title="Time to Donate!",
            status='sent',
            is_read=False
        )
        return notification
    except:
        return None


def send_request_fulfilled(donor_user, blood_type, location):
    """
    Notify a donor that their request has been fulfilled.
    
    Args:
        donor_user: Django User object
        blood_type (str): Blood type that was needed
        location (str): Location where blood was needed
    
    Returns:
        Notification: Created notification object or None
    """
    try:
        message = f"Good news! The {blood_type} blood request at {location} has been fulfilled. Thank you for your contribution to this emergency!"
        
        notification = Notification.objects.create(
            recipient=donor_user,
            notification_type='request_fulfilled',
            message=message,
            blood_type=blood_type,
            location=location,
            title="Emergency Request Fulfilled",
            status='sent',
            is_read=False
        )
        return notification
    except:
        return None


def mark_notification_as_read(notification):
    """
    Mark a notification as read.
    
    Args:
        notification: Notification object to mark as read
    
    Returns:
        Notification: Updated notification object
    """
    notification.is_read = True
    notification.status = 'read'
    notification.read_at = timezone.now()
    notification.save()
    return notification


def get_unread_notifications_count(user):
    """
    Get count of unread notifications for a user.
    
    Args:
        user: Django User object
    
    Returns:
        int: Count of unread notifications
    """
    return Notification.objects.filter(
        recipient=user,
        is_read=False
    ).count()
