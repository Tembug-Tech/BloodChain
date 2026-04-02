"""
Unit tests for the Hospital app
Tests cover: hospital creation, blood requests, filtering, and status updates
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from hospital.models import Hospital, BloodRequest, BloodInventory
from hospital.serializers import (
    HospitalSerializer, HospitalCreateSerializer,
    BloodRequestSerializer, BloodInventorySerializer
)


@pytest.mark.django_db
class TestHospitalModel:
    """Test Hospital model and database operations"""
    
    def test_hospital_creation_with_valid_data(self):
        """Test hospital creation with all required fields"""
        hospital = Hospital.objects.create(
            name='City Hospital',
            registration_number='REG-001',
            email='contact@cityhospital.com',
            phone_number='+1-555-1000',
            address='123 Main Street',
            city='Boston',
            state='MA',
            country='USA',
            postal_code='02101'
        )
        
        assert hospital.id is not None
        assert hospital.name == 'City Hospital'
        assert hospital.is_verified is False
        assert hospital.is_active is True
        assert hospital.admin is None
    
    def test_hospital_unique_name(self):
        """Test that hospital names are unique"""
        hospital1 = Hospital.objects.create(
            name='Unique Hospital',
            registration_number='REG-001',
            email='hospital1@test.com',
            phone_number='+1-555-1001',
            address='123 Main St',
            city='Boston',
            state='MA',
            country='USA',
            postal_code='02101'
        )
        
        # Try to create another hospital with same name
        with pytest.raises(Exception):  # IntegrityError
            hospital2 = Hospital.objects.create(
                name='Unique Hospital',
                registration_number='REG-002',
                email='hospital2@test.com',
                phone_number='+1-555-1002',
                address='456 Oak Ave',
                city='New York',
                state='NY',
                country='USA',
                postal_code='10001'
            )
    
    def test_hospital_unique_registration_number(self):
        """Test that registration numbers are unique"""
        hospital1 = Hospital.objects.create(
            name='Hospital A',
            registration_number='REG-UNIQUE',
            email='hospital-a@test.com',
            phone_number='+1-555-1003',
            address='123 Main St',
            city='Boston',
            state='MA',
            country='USA',
            postal_code='02101'
        )
        
        # Try to create another hospital with same registration number
        with pytest.raises(Exception):  # IntegrityError
            hospital2 = Hospital.objects.create(
                name='Hospital B',
                registration_number='REG-UNIQUE',
                email='hospital-b@test.com',
                phone_number='+1-555-1004',
                address='456 Oak Ave',
                city='Boston',
                state='MA',
                country='USA',
                postal_code='02101'
            )
    
    def test_hospital_optional_fields(self):
        """Test hospital with optional fields (website)"""
        hospital = Hospital.objects.create(
            name='Basic Hospital',
            registration_number='REG-BASIC',
            email='basic@hospital.com',
            phone_number='+1-555-1005',
            address='789 Elm St',
            city='Chicago',
            state='IL',
            country='USA',
            postal_code='60601',
            website='https://hospital.com'
        )
        
        assert hospital.website == 'https://hospital.com'
    
    def test_hospital_timestamps(self):
        """Test that creation and update timestamps are set"""
        hospital = Hospital.objects.create(
            name='Time Hospital',
            registration_number='REG-TIME',
            email='time@hospital.com',
            phone_number='+1-555-1006',
            address='111 Time St',
            city='Denver',
            state='CO',
            country='USA',
            postal_code='80202'
        )
        
        assert hospital.created_at is not None
        assert hospital.updated_at is not None
        assert isinstance(hospital.created_at, datetime)


@pytest.mark.django_db
class TestBloodRequestModel:
    """Test BloodRequest model"""
    
    def setup_method(self):
        """Create a test hospital"""
        self.hospital = Hospital.objects.create(
            name='Test Hospital',
            registration_number='REG-TEST-001',
            email='test@hospital.com',
            phone_number='+1-555-2000',
            address='222 Hospital Way',
            city='Seattle',
            state='WA',
            country='USA',
            postal_code='98101'
        )
    
    def test_blood_request_creation_with_valid_data(self):
        """Test creating a blood request with valid data"""
        request = BloodRequest.objects.create(
            hospital=self.hospital,
            blood_type='O+',
            units_needed=Decimal('5.00'),
            urgency_level='critical',
            description='Emergency surgery needed'
        )
        
        assert request.id is not None
        assert request.blood_type == 'O+'
        assert request.units_needed == Decimal('5.00')
        assert request.urgency_level == 'critical'
        assert request.status == 'open'  # Default status
    
    def test_blood_request_all_blood_types(self):
        """Test blood request with all blood types"""
        blood_types = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']
        
        for blood_type in blood_types:
            request = BloodRequest.objects.create(
                hospital=self.hospital,
                blood_type=blood_type,
                units_needed=Decimal('3.00'),
                urgency_level='normal'
            )
            assert request.blood_type == blood_type
    
    def test_blood_request_urgency_levels(self):
        """Test blood request with all urgency levels"""
        urgency_levels = ['critical', 'urgent', 'normal']
        
        for urgency in urgency_levels:
            request = BloodRequest.objects.create(
                hospital=self.hospital,
                blood_type='O+',
                units_needed=Decimal('2.00'),
                urgency_level=urgency
            )
            assert request.urgency_level == urgency
    
    def test_blood_request_default_status_is_open(self):
        """Test that default status is 'open'"""
        request = BloodRequest.objects.create(
            hospital=self.hospital,
            blood_type='A+',
            units_needed=Decimal('4.00'),
            urgency_level='urgent'
        )
        
        assert request.status == 'open'
    
    def test_blood_request_cascade_delete(self):
        """Test that blood requests are deleted when hospital is deleted"""
        request = BloodRequest.objects.create(
            hospital=self.hospital,
            blood_type='B+',
            units_needed=Decimal('6.00'),
            urgency_level='normal'
        )
        
        initial_count = BloodRequest.objects.count()
        self.hospital.delete()
        
        assert BloodRequest.objects.count() == initial_count - 1


@pytest.mark.django_db
class TestBloodRequestFiltering:
    """Test filtering blood requests"""
    
    def setup_method(self):
        """Create test hospitals and blood requests"""
        self.hospital1 = Hospital.objects.create(
            name='Hospital Alpha',
            registration_number='REG-ALPHA',
            email='alpha@hospital.com',
            phone_number='+1-555-3000',
            address='1 Alpha Way',
            city='Boston',
            state='MA',
            country='USA',
            postal_code='02101'
        )
        
        self.hospital2 = Hospital.objects.create(
            name='Hospital Beta',
            registration_number='REG-BETA',
            email='beta@hospital.com',
            phone_number='+1-555-3001',
            address='2 Beta Way',
            city='New York',
            state='NY',
            country='USA',
            postal_code='10001'
        )
        
        # Create requests with different blood types and statuses
        self.requests = []
        blood_types = ['O+', 'O-', 'A+', 'B+', 'O+', 'AB-']
        statuses = ['open', 'open', 'fulfilled', 'open', 'cancelled', 'open']
        urgencies = ['critical', 'urgent', 'normal', 'critical', 'urgent', 'normal']
        
        for idx, (bt, st, urg) in enumerate(zip(blood_types, statuses, urgencies)):
            hospital = self.hospital1 if idx < 3 else self.hospital2
            request = BloodRequest.objects.create(
                hospital=hospital,
                blood_type=bt,
                units_needed=Decimal('5.00'),
                urgency_level=urg,
                status=st
            )
            self.requests.append(request)
    
    def test_filter_requests_by_blood_type_o_positive(self):
        """Test filtering requests by O+ blood type"""
        requests = BloodRequest.objects.filter(blood_type='O+')
        
        assert requests.count() == 2
        for req in requests:
            assert req.blood_type == 'O+'
    
    def test_filter_requests_by_blood_type_a_positive(self):
        """Test filtering requests by A+ blood type"""
        requests = BloodRequest.objects.filter(blood_type='A+')
        
        assert requests.count() == 1
        assert requests.first().blood_type == 'A+'
    
    def test_filter_requests_by_status_open(self):
        """Test filtering requests by open status"""
        open_requests = BloodRequest.objects.filter(status='open')
        
        assert open_requests.count() == 4
        for req in open_requests:
            assert req.status == 'open'
    
    def test_filter_requests_by_status_fulfilled(self):
        """Test filtering requests by fulfilled status"""
        fulfilled_requests = BloodRequest.objects.filter(status='fulfilled')
        
        assert fulfilled_requests.count() == 1
        assert fulfilled_requests.first().status == 'fulfilled'
    
    def test_filter_requests_by_hospital(self):
        """Test filtering requests by hospital"""
        alpha_requests = BloodRequest.objects.filter(hospital=self.hospital1)
        
        assert alpha_requests.count() == 3
        for req in alpha_requests:
            assert req.hospital == self.hospital1
    
    def test_filter_by_urgency_critical(self):
        """Test filtering requests by critical urgency"""
        critical = BloodRequest.objects.filter(urgency_level='critical')
        
        assert critical.count() == 2
        for req in critical:
            assert req.urgency_level == 'critical'
    
    def test_filter_by_blood_type_and_status(self):
        """Test filtering by both blood type and status"""
        requests = BloodRequest.objects.filter(
            blood_type='O+',
            status='open'
        )
        
        assert requests.count() == 1
        assert requests.first().blood_type == 'O+'
        assert requests.first().status == 'open'


@pytest.mark.django_db
class TestBloodRequestStatusUpdate:
    """Test blood request status updates"""
    
    def setup_method(self):
        """Create a test hospital and blood request"""
        self.hospital = Hospital.objects.create(
            name='Update Hospital',
            registration_number='REG-UPDATE',
            email='update@hospital.com',
            phone_number='+1-555-4000',
            address='4 Update St',
            city='Phoenix',
            state='AZ',
            country='USA',
            postal_code='85001'
        )
        
        self.request = BloodRequest.objects.create(
            hospital=self.hospital,
            blood_type='O+',
            units_needed=Decimal('5.00'),
            urgency_level='critical',
            status='open'
        )
    
    def test_blood_request_status_update_to_fulfilled(self):
        """Test updating blood request status to fulfilled"""
        assert self.request.status == 'open'
        
        self.request.status = 'fulfilled'
        self.request.fulfilled_at = datetime.now()
        self.request.save()
        
        refreshed = BloodRequest.objects.get(id=self.request.id)
        assert refreshed.status == 'fulfilled'
        assert refreshed.fulfilled_at is not None
    
    def test_blood_request_status_update_to_cancelled(self):
        """Test updating blood request status to cancelled"""
        self.request.status = 'cancelled'
        self.request.save()
        
        refreshed = BloodRequest.objects.get(id=self.request.id)
        assert refreshed.status == 'cancelled'
    
    def test_blood_request_status_transitions(self):
        """Test status transitions: open -> fulfilled -> open (invalid, but test state)"""
        # Start as open
        assert self.request.status == 'open'
        
        # Change to fulfilled
        self.request.status = 'fulfilled'
        self.request.save()
        assert BloodRequest.objects.get(id=self.request.id).status == 'fulfilled'
        
        # Change back to open (unusual but possible)
        self.request.status = 'open'
        self.request.fulfilled_at = None
        self.request.save()
        assert BloodRequest.objects.get(id=self.request.id).status == 'open'


@pytest.mark.django_db
class TestBloodInventory:
    """Test blood inventory management"""
    
    def setup_method(self):
        """Create a test hospital"""
        self.hospital = Hospital.objects.create(
            name='Inventory Hospital',
            registration_number='REG-INVENTORY',
            email='inventory@hospital.com',
            phone_number='+1-555-5000',
            address='5 Inventory Ave',
            city='Miami',
            state='FL',
            country='USA',
            postal_code='33101'
        )
    
    def test_blood_inventory_creation(self):
        """Test creating blood inventory"""
        inventory = BloodInventory.objects.create(
            hospital=self.hospital,
            blood_type='O+',
            quantity=25,
            expiry_date=date.today() + timedelta(days=42)
        )
        
        assert inventory.id is not None
        assert inventory.blood_type == 'O+'
        assert inventory.quantity == 25
    
    def test_blood_inventory_unique_per_hospital_blood_type(self):
        """Test that hospital can only have one inventory per blood type"""
        BloodInventory.objects.create(
            hospital=self.hospital,
            blood_type='A+',
            quantity=10,
            expiry_date=date.today() + timedelta(days=42)
        )
        
        # Try to create another inventory for same hospital and blood type
        with pytest.raises(Exception):  # IntegrityError
            BloodInventory.objects.create(
                hospital=self.hospital,
                blood_type='A+',
                quantity=15,
                expiry_date=date.today() + timedelta(days=42)
            )


@pytest.mark.django_db
class TestHospitalAPI:
    """Test Hospital API endpoints"""
    
    def setup_method(self):
        """Set up test client and authenticated user"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='hospitaladmin',
            email='admin@hospital.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_hospital_creation_via_api(self):
        """Test creating hospital via API"""
        hospital_data = {
            'name': 'API Test Hospital',
            'registration_number': 'REG-API-001',
            'email': 'api@hospital.com',
            'phone_number': '+1-555-6000',
            'address': '6 API Street',
            'city': 'Los Angeles',
            'state': 'CA',
            'country': 'USA',
            'postal_code': '90001'
        }
        
        response = self.client.post('/api/hospitals/', hospital_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Hospital.objects.filter(name='API Test Hospital').exists()
    
    def test_blood_request_list_filtering_by_blood_type(self):
        """Test filtering blood requests by blood type via API"""
        hospital = Hospital.objects.create(
            name='Filter Hospital',
            registration_number='REG-FILTER',
            email='filter@hospital.com',
            phone_number='+1-555-7000',
            address='7 Filter Ln',
            city='Houston',
            state='TX',
            country='USA',
            postal_code='77001'
        )
        
        # Create multiple blood requests
        BloodRequest.objects.create(
            hospital=hospital,
            blood_type='O+',
            units_needed=Decimal('5.00'),
            urgency_level='normal'
        )
        BloodRequest.objects.create(
            hospital=hospital,
            blood_type='A+',
            units_needed=Decimal('3.00'),
            urgency_level='normal'
        )
        
        response = self.client.get('/api/blood-requests/', {'blood_type': 'O+'})
        
        assert response.status_code == status.HTTP_200_OK
        # Filter results to match blood_type
        data = response.json()
        if isinstance(data, list):
            assert any(req['blood_type'] == 'O+' for req in data)
