from rest_framework import serializers
from .models import BloodUnit, BloodDonation, BloodTransfer


class BloodUnitSerializer(serializers.ModelSerializer):
    """Basic serializer for blood units"""
    donor_name = serializers.CharField(source='donor.user.get_full_name', read_only=True)
    donor_blood_type = serializers.CharField(source='donor.blood_type', read_only=True)
    hospital_name = serializers.CharField(source='current_hospital.name', read_only=True, allow_null=True)
    
    class Meta:
        model = BloodUnit
        fields = [
            'id', 'unit_id', 'donor', 'donor_name', 'blood_type', 'donor_blood_type',
            'collected_at', 'expiry_date', 'current_hospital', 'hospital_name',
            'status', 'hiv_test', 'hepatitis_test', 'blockchain_tx_hash', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'unit_id', 'created_at', 'updated_at']


class BloodUnitDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for blood units with full lifecycle history"""
    donor_info = serializers.SerializerMethodField(read_only=True)
    location_info = serializers.SerializerMethodField(read_only=True)
    lifecycle_summary = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = BloodUnit
        fields = [
            'id', 'unit_id', 'donor', 'donor_info', 'blood_type',
            'collected_at', 'expiry_date', 'current_hospital', 'location_info',
            'status', 'hiv_test', 'hepatitis_test', 'blockchain_tx_hash',
            'status_history', 'lifecycle_summary', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'unit_id', 'status_history', 'created_at', 'updated_at']
    
    def get_donor_info(self, obj):
        """Get detailed donor information"""
        if obj.donor:
            return {
                'id': obj.donor.id,
                'name': obj.donor.user.get_full_name(),
                'email': obj.donor.user.email,
                'blood_type': obj.donor.blood_type,
                'location': obj.donor.location,
                'phone': obj.donor.phone_number,
            }
        return None
    
    def get_location_info(self, obj):
        """Get detailed location information"""
        if obj.current_hospital:
            return {
                'id': obj.current_hospital.id,
                'name': obj.current_hospital.name,
                'email': obj.current_hospital.email,
                'phone': obj.current_hospital.phone_number,
                'address': obj.current_hospital.address,
                'city': obj.current_hospital.city,
                'state': obj.current_hospital.state,
            }
        return None
    
    def get_lifecycle_summary(self, obj):
        """Get lifecycle summary including all status changes"""
        summary = {
            'initial_status': 'collected',
            'current_status': obj.status,
            'status_changes': obj.status_history if obj.status_history else [],
            'total_changes': len(obj.status_history) if obj.status_history else 0,
            'days_in_storage': (obj.expiry_date - obj.collected_at).days,
            'is_expired': False,
        }
        
        from django.utils import timezone
        if obj.expiry_date < timezone.now():
            summary['is_expired'] = True
        
        return summary


class BloodUnitCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating blood units"""
    class Meta:
        model = BloodUnit
        fields = [
            'donor', 'blood_type', 'collected_at', 'expiry_date',
            'current_hospital', 'hiv_test', 'hepatitis_test'
        ]
    
    def validate(self, data):
        """Validate that expiry_date is after collected_at"""
        if data['expiry_date'] <= data['collected_at']:
            raise serializers.ValidationError(
                "Expiry date must be after collection date"
            )
        return data


class BloodUnitStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating blood unit status"""
    class Meta:
        model = BloodUnit
        fields = ['status', 'current_hospital', 'blockchain_tx_hash']


class BloodDonationSerializer(serializers.ModelSerializer):
    donor_name = serializers.CharField(source='donor.user.get_full_name', read_only=True)
    hospital_name = serializers.CharField(source='hospital.name', read_only=True)
    blood_type = serializers.CharField(source='donor.blood_type', read_only=True)
    
    class Meta:
        model = BloodDonation
        fields = [
            'id', 'donor', 'donor_name', 'blood_type', 'hospital', 'hospital_name',
            'donation_date', 'status', 'blood_units', 'blockchain_hash', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'blockchain_hash']


class BloodTransferSerializer(serializers.ModelSerializer):
    donation_info = BloodDonationSerializer(source='donation', read_only=True)
    from_hospital_name = serializers.CharField(source='from_hospital.name', read_only=True)
    to_hospital_name = serializers.CharField(source='to_hospital.name', read_only=True)
    
    class Meta:
        model = BloodTransfer
        fields = [
            'id', 'donation', 'donation_info', 'from_hospital', 'from_hospital_name',
            'to_hospital', 'to_hospital_name', 'transfer_type', 'status', 'transfer_date',
            'received_date', 'blockchain_hash', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'blockchain_hash']
