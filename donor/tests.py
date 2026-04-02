"""
Unit tests for the Donor app
Tests cover: registration, validation, filtering, and availability updates
"""

import pytest
from datetime import date, datetime, timedelta
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from donor.models import Donor
from donor.serializers import DonorRegistrationSerializer, DonorSerializer


@pytest.mark.django_db
class TestDonorModel:
    """Test Donor model and database operations"""
    
    def setup_method(self):
        """Set up test fixtures for each test"""
        self.user = User.objects.create_user(
            username='testdonor',
            email='donor@test.com',
            password='testpassword123',
            first_name='John',
            last_name='Doe'
        )
    
    def test_donor_creation_with_valid_data(self):
        """Test donor registration with all valid data"""
        donor = Donor.objects.create(
            user=self.user,
            blood_type='O+',
            phone_number='+1-555-0001',
            location='Boston, MA',
            date_of_birth=date(1990, 5, 15),
            is_available=True,
            wallet_address='0x742d35Cc6634C0532925a3b844Bc9e7595f42e1'
        )
        
        assert donor.id is not None
        assert donor.user.username == 'testdonor'
        assert donor.blood_type == 'O+'
        assert donor.is_available is True
        assert donor.phone_number == '+1-555-0001'
        assert str(donor) == 'John Doe - O+'
    
    def test_donor_creation_with_invalid_blood_type(self):
        """Test that invalid blood type raises validation error"""
        with pytest.raises(ValueError):
            donor = Donor.objects.create(
                user=self.user,
                blood_type='XYZ',  # Invalid blood type
                phone_number='+1-555-0001',
                location='Boston, MA',
                date_of_birth=date(1990, 5, 15)
            )
    
    def test_donor_all_blood_types(self):
        """Test donor creation with all valid blood types"""
        blood_types = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']
        
        for idx, blood_type in enumerate(blood_types):
            user = User.objects.create_user(
                username=f'donor{idx}',
                email=f'donor{idx}@test.com',
                password='testpassword123'
            )
            donor = Donor.objects.create(
                user=user,
                blood_type=blood_type,
                phone_number='+1-555-0001',
                location='Boston, MA',
                date_of_birth=date(1990, 5, 15)
            )
            assert donor.blood_type == blood_type
    
    def test_donor_created_at_timestamp(self):
        """Test that created_at timestamp is automatically set"""
        donor = Donor.objects.create(
            user=self.user,
            blood_type='O+',
            phone_number='+1-555-0001',
            location='Boston, MA',
            date_of_birth=date(1990, 5, 15)
        )
        
        assert donor.created_at is not None
        assert donor.updated_at is not None
        assert isinstance(donor.created_at, datetime)
    
    def test_donor_last_donation_date_optional(self):
        """Test that last_donation_date is optional"""
        donor = Donor.objects.create(
            user=self.user,
            blood_type='O+',
            phone_number='+1-555-0001',
            location='Boston, MA',
            date_of_birth=date(1990, 5, 15)
        )
        
        assert donor.last_donation_date is None
    
    def test_donor_availability_default_true(self):
        """Test that is_available defaults to True"""
        donor = Donor.objects.create(
            user=self.user,
            blood_type='O+',
            phone_number='+1-555-0001',
            location='Boston, MA',
            date_of_birth=date(1990, 5, 15)
        )
        
        assert donor.is_available is True
    
    def test_donor_wallet_address_optional(self):
        """Test that wallet_address is optional"""
        donor = Donor.objects.create(
            user=self.user,
            blood_type='O+',
            phone_number='+1-555-0001',
            location='Boston, MA',
            date_of_birth=date(1990, 5, 15)
        )
        
        assert donor.wallet_address is None


@pytest.mark.django_db
class TestDonorFiltering:
    """Test donor filtering and querying"""
    
    def setup_method(self):
        """Create test donors with different blood types and locations"""
        blood_types = ['O+', 'A+', 'B+', 'AB+', 'O-', 'A-']
        locations = ['Boston, MA', 'New York, NY', 'Chicago, IL', 'Boston, MA', 'New York, NY', 'Denver, CO']
        
        for idx, (bt, loc) in enumerate(zip(blood_types, locations)):
            user = User.objects.create_user(
                username=f'donor{idx}',
                email=f'donor{idx}@test.com',
                password='testpassword123'
            )
            Donor.objects.create(
                user=user,
                blood_type=bt,
                phone_number=f'+1-555-000{idx}',
                location=loc,
                date_of_birth=date(1990, 5, 15),
                is_available=(idx % 2 == 0)  # Half available, half not
            )
    
    def test_list_donors_by_blood_type_o_positive(self):
        """Test filtering donors by O+ blood type"""
        donors = Donor.objects.filter(blood_type='O+')
        
        assert donors.count() == 1
        assert donors.first().blood_type == 'O+'
    
    def test_list_donors_by_blood_type_a_positive(self):
        """Test filtering donors by A+ blood type"""
        donors = Donor.objects.filter(blood_type='A+')
        
        assert donors.count() == 1
        assert donors.first().blood_type == 'A+'
    
    def test_list_available_donors(self):
        """Test filtering only available donors"""
        available_donors = Donor.objects.filter(is_available=True)
        
        assert available_donors.count() == 3  # Half of 6
        for donor in available_donors:
            assert donor.is_available is True
    
    def test_list_available_donors_by_blood_type(self):
        """Test filtering available donors by blood type"""
        available_o_plus = Donor.objects.filter(
            blood_type='O+',
            is_available=True
        )
        
        assert available_o_plus.count() == 1
        assert available_o_plus.first().blood_type == 'O+'
        assert available_o_plus.first().is_available is True
    
    def test_list_donors_by_location(self):
        """Test filtering donors by location"""
        boston_donors = Donor.objects.filter(location__icontains='Boston')
        
        assert boston_donors.count() == 2
        for donor in boston_donors:
            assert 'Boston' in donor.location
    
    def test_list_donors_by_location_and_blood_type(self):
        """Test filtering donors by both location and blood type"""
        donors = Donor.objects.filter(
            location__icontains='Boston',
            blood_type='O+'
        )
        
        assert donors.count() == 1
        assert donors.first().blood_type == 'O+'
        assert 'Boston' in donors.first().location
    
    def test_donors_ordering(self):
        """Test that donors are ordered by creation date descending"""
        donors = list(Donor.objects.all())
        
        # Should be ordered by creation date (newest first)
        assert donors[0].created_at >= donors[-1].created_at


@pytest.mark.django_db
class TestDonorAvailabilityUpdate:
    """Test donor availability status updates"""
    
    def setup_method(self):
        """Create a test donor"""
        self.user = User.objects.create_user(
            username='testdonor',
            email='donor@test.com',
            password='testpassword123'
        )
        self.donor = Donor.objects.create(
            user=self.user,
            blood_type='O+',
            phone_number='+1-555-0001',
            location='Boston, MA',
            date_of_birth=date(1990, 5, 15),
            is_available=True
        )
    
    def test_donor_availability_update_to_false(self):
        """Test updating donor availability from True to False"""
        assert self.donor.is_available is True
        
        self.donor.is_available = False
        self.donor.save()
        
        refreshed_donor = Donor.objects.get(id=self.donor.id)
        assert refreshed_donor.is_available is False
    
    def test_donor_availability_update_to_true(self):
        """Test updating donor availability from False to True"""
        self.donor.is_available = False
        self.donor.save()
        
        self.donor.is_available = True
        self.donor.save()
        
        refreshed_donor = Donor.objects.get(id=self.donor.id)
        assert refreshed_donor.is_available is True
    
    def test_donor_availability_toggle(self):
        """Test multiple availability toggles"""
        for i in range(5):
            is_available = (i % 2 == 0)
            self.donor.is_available = is_available
            self.donor.save()
            
            refreshed = Donor.objects.get(id=self.donor.id)
            assert refreshed.is_available == is_available
    
    def test_last_donation_date_update(self):
        """Test updating last donation date"""
        assert self.donor.last_donation_date is None
        
        now = datetime.now()
        self.donor.last_donation_date = now
        self.donor.save()
        
        refreshed_donor = Donor.objects.get(id=self.donor.id)
        assert refreshed_donor.last_donation_date is not None
    
    def test_updated_at_changes_on_save(self):
        """Test that updated_at timestamp changes when donor is updated"""
        original_updated_at = self.donor.updated_at
        
        # Wait a moment to ensure timestamp difference
        import time
        time.sleep(0.01)
        
        self.donor.is_available = False
        self.donor.save()
        
        refreshed_donor = Donor.objects.get(id=self.donor.id)
        assert refreshed_donor.updated_at > original_updated_at


@pytest.mark.django_db
class TestDonorAPIRegistration:
    """Test Donor registration API endpoints"""
    
    def setup_method(self):
        """Set up test client"""
        self.client = APIClient()
    
    def test_donor_registration_with_valid_data(self):
        """Test successful donor registration via API"""
        registration_data = {
            'username': 'johndoe',
            'email': 'john@example.com',
            'password': 'strongpassword123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'blood_type': 'O+',
            'phone_number': '+1-555-0001',
            'location': 'Boston, MA',
            'date_of_birth': '1990-05-15',
            'is_available': True
        }
        
        response = self.client.post('/api/donors/register/', registration_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username='johndoe').exists()
        assert Donor.objects.filter(blood_type='O+').exists()
    
    def test_donor_registration_with_missing_blood_type(self):
        """Test registration fails when blood type is missing"""
        registration_data = {
            'username': 'janedoe',
            'email': 'jane@example.com',
            'password': 'strongpassword123!',
            'phone_number': '+1-555-0002',
            'location': 'New York, NY',
            'date_of_birth': '1995-08-20'
        }
        
        response = self.client.post('/api/donors/register/', registration_data)
        
        # Should fail validation because blood_type is required
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_donor_registration_with_invalid_blood_type(self):
        """Test registration fails with invalid blood type"""
        registration_data = {
            'username': 'testdoner',
            'email': 'test@example.com',
            'password': 'strongpassword123!',
            'blood_type': 'INVALID',  # Invalid blood type
            'phone_number': '+1-555-0003',
            'location': 'Chicago, IL',
            'date_of_birth': '1992-12-10'
        }
        
        response = self.client.post('/api/donors/register/', registration_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_donor_registration_with_duplicate_username(self):
        """Test registration fails with duplicate username"""
        # Create first donor
        User.objects.create_user(
            username='duplicate',
            email='first@example.com',
            password='password123'
        )
        
        # Try to register with same username
        registration_data = {
            'username': 'duplicate',
            'email': 'second@example.com',
            'password': 'strongpassword123!',
            'blood_type': 'A+',
            'phone_number': '+1-555-0004',
            'location': 'Denver, CO',
            'date_of_birth': '1993-03-21'
        }
        
        response = self.client.post('/api/donors/register/', registration_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestDonorSerializer:
    """Test Donor serializer"""
    
    def setup_method(self):
        """Create a test donor"""
        self.user = User.objects.create_user(
            username='testdonor',
            email='donor@test.com',
            password='testpassword123',
            first_name='John',
            last_name='Doe'
        )
        self.donor = Donor.objects.create(
            user=self.user,
            blood_type='O+',
            phone_number='+1-555-0001',
            location='Boston, MA',
            date_of_birth=date(1990, 5, 15),
            is_available=True,
            wallet_address='0x742d35Cc6634C0532925a3b844Bc9e7595f42e1'
        )
    
    def test_donor_serializer_output(self):
        """Test DonorSerializer correctly serializes donor object"""
        serializer = DonorSerializer(self.donor)
        data = serializer.data
        
        assert data['blood_type'] == 'O+'
        assert data['phone_number'] == '+1-555-0001'
        assert data['location'] == 'Boston, MA'
        assert data['is_available'] is True
    
    def test_donor_registration_serializer_validation(self):
        """Test DonorRegistrationSerializer validation"""
        valid_data = {
            'username': 'newdonor',
            'email': 'new@example.com',
            'password': 'strongpassword123!',
            'blood_type': 'A+',
            'phone_number': '+1-555-0005',
            'location': 'Seattle, WA',
            'date_of_birth': '1994-07-10'
        }
        
        serializer = DonorRegistrationSerializer(data=valid_data)
        assert serializer.is_valid()


@pytest.mark.django_db
class TestDonorQueries:
    """Test donor query performance and complex queries"""
    
    def setup_method(self):
        """Create multiple donors for testing"""
        for i in range(10):
            user = User.objects.create_user(
                username=f'donor{i}',
                email=f'donor{i}@test.com',
                password='testpassword123'
            )
            Donor.objects.create(
                user=user,
                blood_type=['O+', 'A+', 'B+', 'AB+'][i % 4],
                phone_number=f'+1-555-{i:04d}',
                location=['Boston', 'New York', 'Chicago'][i % 3],
                date_of_birth=date(1990 + (i % 10), 5, 15),
                is_available=(i % 2 == 0)
            )
    
    def test_count_available_donors(self):
        """Test counting available donors"""
        count = Donor.objects.filter(is_available=True).count()
        assert count == 5  # Half of 10
    
    def test_count_donors_by_blood_type(self):
        """Test counting donors by blood type"""
        o_plus_count = Donor.objects.filter(blood_type='O+').count()
        assert o_plus_count == 3  # 10 % 4 = 3 for O+
    
    def test_get_random_available_donor(self):
        """Test getting a random available donor"""
        donor = Donor.objects.filter(is_available=True).first()
        assert donor is not None
        assert donor.is_available is True
    
    def test_exclude_unavailable_donors(self):
        """Test excluding unavailable donors"""
        available = Donor.objects.filter(is_available=True)
        unavailable = Donor.objects.filter(is_available=False)
        
        assert available.count() + unavailable.count() == 10
        
        for donor in available:
            assert donor.is_available is True
        for donor in unavailable:
            assert donor.is_available is False
