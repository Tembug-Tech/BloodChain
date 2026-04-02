from django.db import models
from django.contrib.auth.models import User
from donor.models import Donor


class Badge(models.Model):
    """Model for donor badges/achievements"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon_url = models.URLField(blank=True)
    criteria = models.CharField(max_length=255)
    points_reward = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class DonorBadge(models.Model):
    """Model for donor badges earned"""
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='earned_badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['donor', 'badge']
        ordering = ['-earned_date']
    
    def __str__(self):
        return f"{self.donor} - {self.badge}"


class Points(models.Model):
    """Model for donor points"""
    POINT_SOURCE_CHOICES = [
        ('donation', 'Blood Donation'),
        ('badge', 'Badge Achievement'),
        ('referral', 'Referral'),
        ('participation', 'Event Participation'),
        ('admin_award', 'Admin Award'),
    ]
    
    donor = models.OneToOneField(Donor, on_delete=models.CASCADE, related_name='points')
    total_points = models.IntegerField(default=0)
    redeemed_points = models.IntegerField(default=0)
    available_points = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Points'
    
    def __str__(self):
        return f"{self.donor} - {self.available_points} points"


class PointTransaction(models.Model):
    """Model for point transactions"""
    POINT_SOURCE_CHOICES = [
        ('donation', 'Blood Donation'),
        ('badge', 'Badge Achievement'),
        ('referral', 'Referral'),
        ('participation', 'Event Participation'),
        ('admin_award', 'Admin Award'),
        ('redemption', 'Redemption'),
    ]
    
    points = models.ForeignKey(Points, on_delete=models.CASCADE, related_name='transactions')
    points_amount = models.IntegerField()
    source = models.CharField(max_length=30, choices=POINT_SOURCE_CHOICES)
    description = models.TextField()
    related_object_id = models.IntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['source']),
        ]
    
    def __str__(self):
        return f"{self.points.donor} - {self.points_amount} points - {self.source}"


class Reward(models.Model):
    """Model for redeemable rewards"""
    name = models.CharField(max_length=255)
    description = models.TextField()
    points_cost = models.IntegerField()
    quantity_available = models.IntegerField()
    category = models.CharField(max_length=100)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class RewardRedemption(models.Model):
    """Model for reward redemptions"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='reward_redemptions')
    reward = models.ForeignKey(Reward, on_delete=models.CASCADE)
    points_spent = models.IntegerField()
    quantity = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    redemption_date = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-redemption_date']
    
    def __str__(self):
        return f"{self.donor} - {self.reward} - {self.status}"


class RewardToken(models.Model):
    """Model for blockchain-based reward tokens"""
    REWARD_TYPE_CHOICES = [
        ('donation_reward', 'Donation Reward'),
        ('referral_bonus', 'Referral Bonus'),
        ('achievement_reward', 'Achievement Reward'),
        ('participation_bonus', 'Participation Bonus'),
    ]
    
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='reward_tokens')
    amount = models.IntegerField(help_text='Amount of tokens issued')
    transaction_hash = models.CharField(max_length=255, help_text='Blockchain transaction hash')
    reward_type = models.CharField(max_length=30, choices=REWARD_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['donor']),
            models.Index(fields=['created_at']),
            models.Index(fields=['transaction_hash']),
        ]
    
    def __str__(self):
        return f"{self.donor} - {self.amount} tokens - {self.reward_type}"
