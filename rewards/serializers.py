from rest_framework import serializers
from .models import Badge, DonorBadge, Points, PointTransaction, Reward, RewardRedemption, RewardToken


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ['id', 'name', 'description', 'icon_url', 'criteria', 'points_reward', 'created_at']
        read_only_fields = ['id', 'created_at']


class DonorBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)
    
    class Meta:
        model = DonorBadge
        fields = ['id', 'donor', 'badge', 'earned_date']
        read_only_fields = ['id', 'earned_date']


class PointTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PointTransaction
        fields = [
            'id', 'points', 'points_amount', 'source', 'description',
            'related_object_id', 'related_object_type', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PointsSerializer(serializers.ModelSerializer):
    transactions = PointTransactionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Points
        fields = [
            'id', 'donor', 'total_points', 'redeemed_points', 'available_points',
            'transactions', 'updated_at'
        ]
        read_only_fields = ['id', 'updated_at']


class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = [
            'id', 'name', 'description', 'points_cost', 'quantity_available',
            'category', 'image_url', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RewardRedemptionSerializer(serializers.ModelSerializer):
    reward = RewardSerializer(read_only=True)
    
    class Meta:
        model = RewardRedemption
        fields = [
            'id', 'donor', 'reward', 'points_spent', 'quantity', 'status',
            'redemption_date', 'completion_date', 'notes'
        ]
        read_only_fields = ['id', 'redemption_date']


class RewardTokenSerializer(serializers.ModelSerializer):
    """Serializer for RewardToken blockchain tracking"""
    donor_name = serializers.CharField(source='donor.user.get_full_name', read_only=True)
    reward_type_display = serializers.CharField(source='get_reward_type_display', read_only=True)
    
    class Meta:
        model = RewardToken
        fields = [
            'id', 'donor', 'donor_name', 'amount', 'transaction_hash',
            'reward_type', 'reward_type_display', 'created_at'
        ]
        read_only_fields = ['id', 'transaction_hash', 'created_at']
