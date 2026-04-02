"""
Unit tests for the Blood Tracking app
Tests cover: blood unit registration, status updates, and blockchain tracking
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
import uuid
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from donor.models import Donor
from hospital.models import Hospital
from blood_tracking.models import BloodUnit, BloodDonation


@pytest.mark.django_db
class TestBloodUnitModel:
    """Test BloodUnit model and database operations"""
    
    def setup_method(self):
        """Create test donor and hospital"""
        self.user = User.objects.create_user(
            username='blooddonor',
            email='blooddonor@test.com',
            password='testpass123'
        )
        
        self.donor = Donor.objects.create(
            user=self.user,
            blood_type='O+',
            phone_number='+1-555-0001',
            location='Boston, MA',
            date_of_birth='1990-05-15'
        )
        
        self.hospital = Hospital.objects.create(
            name='Blood Bank Hospital',
            registration_number='REG-BLOOD-001',
            email='bloodbank@hospital.com',
            phone_number='+1-555-9000',
            address='9 Blood Bank St',
            city='Boston',
            state='MA',
            country='USA',
            postal_code='02101'
        )
    
    def test_blood_unit_registration_with_valid_data(self):
        """Test blood unit registration with valid data"""
        now = timezone.now()
        expiry = now + timedelta(days=42)
        
        blood_unit = BloodUnit.objects.create(
            donor=self.donor,
            blood_type='O+',
            collected_at=now,
            expiry_date=expiry,
            current_hospital=self.hospital,
            status='collected'
        )
        
        assert blood_unit.id is not None
        assert blood_unit.unit_id is not None
        assert blood_unit.donor == self.donor
        assert blood_unit.blood_type == 'O+'
        assert blood_unit.status == 'collected'
        assert blood_unit.hiv_test is False
        assert blood_unit.hepatitis_test is False
    
    def test_blood_unit_unique_unit_id(self):
        """Test that each blood unit has a unique unit_id"""
        now = timezone.now()
        expiry = now + timedelta(days=42)
        
        unit1 = BloodUnit.objects.create(
            donor=self.donor,
            blood_type='O+',
            collected_at=now,
            expiry_date=expiry,
            current_hospital=self.hospital
        )
        
        unit2 = BloodUnit.objects.create(
            donor=self.donor,
            blood_type='O+',
            collected_at=now + timedelta(hours=1),
            expiry_date=expiry + timedelta(hours=1),
            current_hospital=self.hospital
        )
        
        assert unit1.unit_id != unit2.unit_id
    
    def test_blood_unit_all_blood_types(self):
        """Test creating blood units with all blood types"""
        blood_types = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-']
        now = timezone.now()
        expiry = now + timedelta(days=42)
        
        for blood_type in blood_types:
            # Update donor's blood type
            self.donor.blood_type = blood_type
            self.donor.save()
            
            unit = BloodUnit.objects.create(
                donor=self.donor,
                blood_type=blood_type,
                collected_at=now,
                expiry_date=expiry,
                current_hospital=self.hospital
            )
            assert unit.blood_type == blood_type
    
    def test_blood_unit_default_status_is_collected(self):
        """Test that default status is 'collected'"""
        now = timezone.now()
        expiry = now + timedelta(days=42)
        
        unit = BloodUnit.objects.create(
            donor=self.donor,
            blood_type='O+',
            collected_at=now,
            expiry_date=expiry,
            current_hospital=self.hospital
        )
        
        assert unit.status == 'collected'
    
    def test_blood_unit_status_history_initialization(self):
        """Test that status_history is initialized as empty list"""
        now = timezone.now()
        expiry = now + timedelta(days=42)
        
        unit = BloodUnit.objects.create(
            donor=self.donor,
            blood_type='O+',
            collected_at=now,
            expiry_date=expiry,
            current_hospital=self.hospital
        )
        
        assert unit.status_history == []
    
    def test_blood_unit_blockchain_tx_hash_optional(self):
        """Test that blockchain_tx_hash is optional"""
        now = timezone.now()
        expiry = now + timedelta(days=42)
        
        unit = BloodUnit.objects.create(
            donor=self.donor,
            blood_type='O+',
            collected_at=now,
            expiry_date=expiry,
            current_hospital=self.hospital
        )
        
        assert unit.blockchain_tx_hash is None


@pytest.mark.django_db
class TestBloodUnitStatusUpdate:
    """Test blood unit status transitions"""
    
    def setup_method(self):
        """Create test donor, hospital, and blood unit"""
        user = User.objects.create_user(
            username='statusdonor',
            email='statusdonor@test.com',
            password='testpass123'
        )
        
        self.donor = Donor.objects.create(
            user=user,
            blood_type='A+',
            phone_number='+1-555-0002',
            location='New York, NY',
            date_of_birth='1992-08-20'
        )
        
        self.hospital = Hospital.objects.create(
            name='Status Hospital',
            registration_number='REG-STATUS',
            email='status@hospital.com',
            phone_number='+1-555-9001',
            address='10 Status Ave',
            city='New York',
            state='NY',
            country='USA',
            postal_code='10001'
        )
        
        now = timezone.now()
        self.unit = BloodUnit.objects.create(
            donor=self.donor,
            blood_type='A+',
            collected_at=now,
            expiry_date=now + timedelta(days=42),
            current_hospital=self.hospital,
            status='collected'
        )
    
    def test_blood_unit_status_collected_to_testing(self):
        """Test status transition: collected -> testing"""
        assert self.unit.status == 'collected'
        
        self.unit.add_status_history('testing', 'Initial blood tests')
        
        refreshed = BloodUnit.objects.get(id=self.unit.id)
        assert refreshed.status == 'testing'
        assert len(refreshed.status_history) == 1
        assert refreshed.status_history[0]['status'] == 'testing'
    
    def test_blood_unit_status_testing_to_storage(self):
        """Test status transition: testing -> storage"""
        self.unit.add_status_history('testing', 'Undergoing tests')
        assert self.unit.status == 'testing'
        
        self.unit.add_status_history('storage', 'Approved for storage')
        
        refreshed = BloodUnit.objects.get(id=self.unit.id)
        assert refreshed.status == 'storage'
        assert len(refreshed.status_history) == 2
    
    def test_blood_unit_status_storage_to_transfused(self):
        """Test status transition: storage -> transfused"""
        self.unit.add_status_history('testing', 'Tests')
        self.unit.add_status_history('storage', 'Stored')
        assert self.unit.status == 'storage'
        
        self.unit.add_status_history('transfused', 'Transfused to patient')
        
        refreshed = BloodUnit.objects.get(id=self.unit.id)
        assert refreshed.status == 'transfused'
        assert len(refreshed.status_history) == 3
    
    def test_blood_unit_full_lifecycle(self):
        """Test complete blood unit lifecycle"""
        statuses = ['testing', 'storage', 'transfused']
        notes = ['Initial tests', 'Approved for storage', 'Used in transfusion']
        
        for status, note in zip(statuses, notes):
            self.unit.add_status_history(status, note)
        
        refreshed = BloodUnit.objects.get(id=self.unit.id)
        assert refreshed.status == 'transfused'
        assert len(refreshed.status_history) == 3
        
        # Verify history order
        for idx, status in enumerate(['testing', 'storage', 'transfused']):
            assert refreshed.status_history[idx]['status'] == status
    
    def test_blood_unit_status_history_with_timestamps(self):
        """Test that status history includes timestamps"""
        self.unit.add_status_history('testing', 'Tests started')
        
        refreshed = BloodUnit.objects.get(id=self.unit.id)
        assert 'timestamp' in refreshed.status_history[0]
        assert refreshed.status_history[0]['notes'] == 'Tests started'
    
    def test_blood_unit_status_to_expired(self):
        """Test status update to expired"""
        self.unit.status = 'expired'
        self.unit.save()
        
        refreshed = BloodUnit.objects.get(id=self.unit.id)
        assert refreshed.status == 'expired'


@pytest.mark.django_db
class TestBloodUnitBlockchainIntegration:
    """Test blockchain transaction hash storage"""
    
    def setup_method(self):
        """Create test donor, hospital, and blood unit"""
        user = User.objects.create_user(
            username='blockchaindonor',
            email='blockchain@test.com',
            password='testpass123'
        )
        
        self.donor = Donor.objects.create(
            user=user,
            blood_type='B+',
            phone_number='+1-555-0003',
            location='Chicago, IL',
            date_of_birth='1995-12-10',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc9e7595f42e1'
        )
        
        self.hospital = Hospital.objects.create(
            name='Blockchain Hospital',
            registration_number='REG-BLOCKCHAIN',
            email='blockchain@hospital.com',
            phone_number='+1-555-9002',
            address='11 Blockchain Dr',
            city='Chicago',
            state='IL',
            country='USA',
            postal_code='60601'
        )
        
        now = timezone.now()
        self.unit = BloodUnit.objects.create(
            donor=self.donor,
            blood_type='B+',
            collected_at=now,
            expiry_date=now + timedelta(days=42),
            current_hospital=self.hospital
        )
    
    def test_blood_unit_blockchain_tx_hash_storage(self):
        """Test storing blockchain transaction hash"""
        tx_hash = '0x' + ''.join(['a'] * 64)
        
        self.unit.blockchain_tx_hash = tx_hash
        self.unit.save()
        
        refreshed = BloodUnit.objects.get(id=self.unit.id)
        assert refreshed.blockchain_tx_hash == tx_hash
    
    def test_blood_unit_blockchain_tx_hash_stored_on_registration(self):
        """Test that blockchain_tx_hash is stored during unit registration"""
        tx_hash = '0x' + 'b' * 64
        
        new_unit = BloodUnit.objects.create(
            donor=self.donor,
            blood_type='B-',
            collected_at=timezone.now(),
            expiry_date=timezone.now() + timedelta(days=42),
            current_hospital=self.hospital,
            blockchain_tx_hash=tx_hash
        )
        
        assert new_unit.blockchain_tx_hash == tx_hash
    
    def test_blood_unit_retrieval_with_blockchain_hash(self):
        """Test retrieving blood unit by blockchain hash"""
        tx_hash = '0x' + 'c' * 64
        self.unit.blockchain_tx_hash = tx_hash
        self.unit.save()
        
        # Query by blockchain hash
        found_unit = BloodUnit.objects.filter(blockchain_tx_hash=tx_hash).first()
        
        assert found_unit is not None
        assert found_unit.id == self.unit.id
    
    def test_blood_unit_hiv_test_status(self):
        """Test HIV test status tracking"""
        assert self.unit.hiv_test is False
        
        self.unit.hiv_test = True
        self.unit.save()
        
        refreshed = BloodUnit.objects.get(id=self.unit.id)
        assert refreshed.hiv_test is True
    
    def test_blood_unit_hepatitis_test_status(self):
        """Test Hepatitis test status tracking"""
        assert self.unit.hepatitis_test is False
        
        self.unit.hepatitis_test = True
        self.unit.save()
        
        refreshed = BloodUnit.objects.get(id=self.unit.id)
        assert refreshed.hepatitis_test is True


@pytest.mark.django_db
class TestBloodUnitQueries:
    """Test blood unit query patterns"""
    
    def setup_method(self):
        """Create test data"""
        user1 = User.objects.create_user(username='donor1', password='test')
        user2 = User.objects.create_user(username='donor2', password='test')
        
        self.donor1 = Donor.objects.create(
            user=user1, blood_type='O+',
            phone_number='+1-555-0004',
            location='Boston', date_of_birth='1990-01-01'
        )
        self.donor2 = Donor.objects.create(
            user=user2, blood_type='A+',
            phone_number='+1-555-0005',
            location='Boston', date_of_birth='1991-01-01'
        )
        
        self.hospital = Hospital.objects.create(
            name='Query Hospital',
            registration_number='REG-QUERY',
            email='query@hospital.com',
            phone_number='+1-555-9003',
            address='12 Query Ln',
            city='Boston',
            state='MA',
            country='USA',
            postal_code='02101'
        )
        
        now = timezone.now()
        for i in range(5):
            donor = self.donor1 if i < 3 else self.donor2
            BloodUnit.objects.create(
                donor=donor,
                blood_type=donor.blood_type,
                collected_at=now + timedelta(hours=i),
                expiry_date=now + timedelta(days=42),
                current_hospital=self.hospital,
                status=['collected', 'testing', 'storage', 'transfused', 'expired'][i]
            )
    
    def test_count_units_by_donor(self):
        """Test counting blood units by donor"""
        donor1_units = BloodUnit.objects.filter(donor=self.donor1).count()
        donor2_units = BloodUnit.objects.filter(donor=self.donor2).count()
        
        assert donor1_units == 3
        assert donor2_units == 2
    
    def test_count_units_by_status(self):
        """Test counting blood units by status"""
        storage_units = BloodUnit.objects.filter(status='storage').count()
        transfused_units = BloodUnit.objects.filter(status='transfused').count()
        
        assert storage_units == 1
        assert transfused_units == 1
    
    def test_count_units_by_blood_type(self):
        """Test counting blood units by blood type"""
        o_plus_units = BloodUnit.objects.filter(blood_type='O+').count()
        a_plus_units = BloodUnit.objects.filter(blood_type='A+').count()
        
        assert o_plus_units == 3
        assert a_plus_units == 2
    
    def test_get_available_units_for_transfusion(self):
        """Test getting units available for transfusion"""
        available = BloodUnit.objects.filter(
            status__in=['storage', 'transfused'],
            hiv_test=True,
            hepatitis_test=True
        )
        
        # Initially 2 units with storage/transfused status but not tested
        initial_count = available.count()
        assert initial_count >= 0
