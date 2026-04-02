from django.db import models
from django.utils import timezone
import uuid
from donor.models import Donor
from hospital.models import Hospital


class BloodUnit(models.Model):
    """Model for individual blood units with lifecycle tracking"""
    STATUS_CHOICES = [
        ('collected', 'Collected'),
        ('testing', 'Testing'),
        ('storage', 'Storage'),
        ('transfused', 'Transfused'),
        ('expired', 'Expired'),
    ]
    
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
    
    unit_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='blood_units')
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)
    collected_at = models.DateTimeField()
    expiry_date = models.DateTimeField()
    current_hospital = models.ForeignKey(
        Hospital, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='blood_units_inventory'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='collected')
    hiv_test = models.BooleanField(default=False)
    hepatitis_test = models.BooleanField(default=False)
    blockchain_tx_hash = models.CharField(max_length=256, blank=True, null=True, help_text='Ethereum transaction hash')
    status_history = models.JSONField(default=list, blank=True, help_text='Status change history')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-collected_at']
        indexes = [
            models.Index(fields=['blood_type']),
            models.Index(fields=['status']),
            models.Index(fields=['donor', 'collected_at']),
            models.Index(fields=['current_hospital', 'status']),
        ]
    
    def __str__(self):
        return f"{self.unit_id} - {self.blood_type} - {self.status}"
    
    def add_status_history(self, new_status, notes=''):
        """Add status change to history"""
        if not self.status_history:
            self.status_history = []
        self.status_history.append({
            'status': new_status,
            'timestamp': timezone.now().isoformat(),
            'notes': notes
        })
        self.status = new_status
        self.save()


class BloodDonation(models.Model):
    """Model for blood donation records"""
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('rejected', 'Rejected'),
    ]
    
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='donations')
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='received_donations')
    donation_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    blood_units = models.DecimalField(max_digits=5, decimal_places=2, default=0.45)
    blockchain_hash = models.CharField(max_length=256, blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-donation_date']
        indexes = [
            models.Index(fields=['donor', 'donation_date']),
            models.Index(fields=['hospital', 'donation_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.donor} - {self.hospital} - {self.donation_date}"


class BloodTransfer(models.Model):
    """Model for blood transfers between hospitals or to patients"""
    TRANSFER_TYPE_CHOICES = [
        ('hospital_to_hospital', 'Hospital to Hospital'),
        ('hospital_to_patient', 'Hospital to Patient'),
        ('bank_to_hospital', 'Bank to Hospital'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_transit', 'In Transit'),
        ('received', 'Received'),
        ('rejected', 'Rejected'),
    ]
    
    donation = models.ForeignKey(BloodDonation, on_delete=models.CASCADE, related_name='transfers')
    from_hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, related_name='outgoing_transfers')
    to_hospital = models.ForeignKey(Hospital, on_delete=models.SET_NULL, null=True, blank=True, related_name='incoming_transfers')
    transfer_type = models.CharField(max_length=20, choices=TRANSFER_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transfer_date = models.DateTimeField()
    received_date = models.DateTimeField(null=True, blank=True)
    blockchain_hash = models.CharField(max_length=256, blank=True, null=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-transfer_date']
        indexes = [
            models.Index(fields=['status', 'transfer_date']),
            models.Index(fields=['from_hospital', 'transfer_date']),
        ]
    
    def __str__(self):
        return f"{self.donation} - {self.transfer_type} - {self.status}"
