from django.db import models
from django.contrib.auth.models import User


class Donor(models.Model):
    """Model for blood donors"""
    BLOOD_TYPE_CHOICES = [
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='donor_profile')
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)
    phone_number = models.CharField(max_length=15)
    location = models.CharField(max_length=255, help_text='City, State or Region')
    date_of_birth = models.DateField()
    last_donation_date = models.DateTimeField(null=True, blank=True)
    is_available = models.BooleanField(default=True, help_text='Donor is available for donation')
    wallet_address = models.CharField(max_length=255, blank=True, null=True, help_text='Blockchain wallet address for token rewards')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['blood_type']),
            models.Index(fields=['is_available']),
            models.Index(fields=['location']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.blood_type}"
