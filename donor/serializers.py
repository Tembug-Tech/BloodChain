from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Donor


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']


class DonorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Donor
        fields = [
            'id', 'user', 'blood_type', 'phone_number', 'location',
            'date_of_birth', 'is_available', 'last_donation_date',
            'wallet_address', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_donation_date']


class DonorRegistrationSerializer(serializers.Serializer):
    """Serializer for donor registration with user account creation"""
    # User fields
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(max_length=128, write_only=True, required=True)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    
    # Donor fields
    blood_type = serializers.ChoiceField(
        choices=Donor.BLOOD_TYPE_CHOICES,
        required=True
    )
    phone_number = serializers.CharField(max_length=15, required=True)
    location = serializers.CharField(max_length=255, required=True)
    date_of_birth = serializers.DateField(required=True)
    is_available = serializers.BooleanField(default=True)
    wallet_address = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        allow_null=True
    )
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    def create(self, validated_data):
        """Create user and donor objects"""
        # Extract user data
        user_data = {
            'username': validated_data.pop('username'),
            'email': validated_data.pop('email'),
            'password': validated_data.pop('password'),
            'first_name': validated_data.pop('first_name', ''),
            'last_name': validated_data.pop('last_name', ''),
        }
        
        # Create user
        user = User.objects.create_user(**user_data)
        
        # Create donor
        donor = Donor.objects.create(user=user, **validated_data)
        return donor
