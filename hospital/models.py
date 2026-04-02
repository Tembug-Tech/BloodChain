from django.db import models
from django.contrib.auth.models import User


class Hospital(models.Model):
    """Model for hospital information"""
    name = models.CharField(max_length=255, unique=True)
    registration_number = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    website = models.URLField(blank=True, null=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='managed_hospital')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_verified']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name


class BloodInventory(models.Model):
    """Model for hospital blood inventory"""
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
    
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='blood_inventory')
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)
    quantity = models.IntegerField(default=0)
    expiry_date = models.DateField()
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['hospital', 'blood_type']
        indexes = [
            models.Index(fields=['blood_type']),
            models.Index(fields=['expiry_date']),
        ]
    
    def __str__(self):
        return f"{self.hospital.name} - {self.blood_type} - {self.quantity} units"


class BloodRequest(models.Model):
    """Model for blood donation requests by hospitals"""
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
    
    URGENCY_CHOICES = [
        ('critical', 'Critical'),
        ('urgent', 'Urgent'),
        ('normal', 'Normal'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
    ]
    
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='blood_requests')
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)
    units_needed = models.DecimalField(max_digits=5, decimal_places=2, help_text='Units of blood needed')
    urgency_level = models.CharField(max_length=20, choices=URGENCY_CHOICES, default='normal')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    description = models.TextField(blank=True, null=True, help_text='Additional details about the request')
    created_at = models.DateTimeField(auto_now_add=True)
    fulfilled_at = models.DateTimeField(null=True, blank=True, help_text='Date when the request was fulfilled')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['blood_type']),
            models.Index(fields=['urgency_level']),
            models.Index(fields=['hospital', 'status']),
        ]
    
    def __str__(self):
        return f"{self.hospital.name} - {self.blood_type} ({self.urgency_level}) - {self.status}"
