from rest_framework import serializers
from .models import Hospital, BloodInventory, BloodRequest


class BloodInventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodInventory
        fields = [
            'id', 'hospital', 'blood_type', 'quantity', 'expiry_date', 'last_updated'
        ]
        read_only_fields = ['id', 'last_updated']


class BloodRequestSerializer(serializers.ModelSerializer):
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)
    
    class Meta:
        model = BloodRequest
        fields = [
            'id', 'hospital', 'hospital_name', 'blood_type', 'units_needed',
            'urgency_level', 'status', 'description', 'created_at', 'fulfilled_at'
        ]
        read_only_fields = ['id', 'created_at', 'fulfilled_at']


class BloodRequestDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for blood requests with full hospital info"""
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)
    hospital_email = serializers.CharField(source='hospital.email', read_only=True)
    hospital_phone = serializers.CharField(source='hospital.phone_number', read_only=True)
    hospital_address = serializers.CharField(source='hospital.address', read_only=True)
    
    class Meta:
        model = BloodRequest
        fields = [
            'id', 'hospital', 'hospital_name', 'hospital_email', 'hospital_phone',
            'hospital_address', 'blood_type', 'units_needed', 'urgency_level',
            'status', 'description', 'created_at', 'fulfilled_at'
        ]
        read_only_fields = ['id', 'created_at', 'fulfilled_at']


class HospitalSerializer(serializers.ModelSerializer):
    blood_inventory = BloodInventorySerializer(many=True, read_only=True)
    blood_requests = BloodRequestSerializer(many=True, read_only=True)
    
    class Meta:
        model = Hospital
        fields = [
            'id', 'name', 'registration_number', 'email', 'phone_number', 'website',
            'address', 'city', 'state', 'country', 'postal_code', 'is_verified',
            'is_active', 'blood_inventory', 'blood_requests', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_verified']


class HospitalCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for hospital creation"""
    class Meta:
        model = Hospital
        fields = [
            'id', 'name', 'registration_number', 'email', 'phone_number',
            'address', 'city', 'state', 'country', 'postal_code', 'website'
        ]
        read_only_fields = ['id']
