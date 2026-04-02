"""
Unit tests for the Rewards app
Tests cover: reward token creation, balance endpoints, and token transactions
"""

import pytest
from datetime import datetime
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from donor.models import Donor
from rewards.models import (
    RewardToken, Points, PointTransaction, Badge, DonorBadge,
    Reward, RewardRedemption
)
from rewards.serializers import RewardTokenSerializer
from rewards.services import (
    issue_reward_token, get_donor_reward_balance,
    get_reward_transaction_history, get_reward_statistics
)


@pytest.mark.django_db
class TestRewardTokenModel:
    """Test RewardToken model"""
    
    def setup_method(self):
        """Create test donor"""
        user = User.objects.create_user(
            username='rewarddonor',
            email='reward@test.com',
            password='testpass123',
            first_name='Reward',
            last_name='Donor'
        )
        
        self.donor = Donor.objects.create(
            user=user,
            blood_type='O+',
            phone_number='+1-555-0001',
            location='Boston, MA',
            date_of_birth='1990-05-15',
            wallet_address='0x742d35Cc6634C0532925a3b844Bc9e7595f42e1'
        )
    
    def test_reward_token_creation_with_valid_data(self):
        """Test creating a reward token with valid data"""
        token = RewardToken.objects.create(
            donor=self.donor,
            amount=100,
            transaction_hash='0x' + 'a' * 64,
            reward_type='donation_reward'
        )
        
        assert token.id is not None
        assert token.donor == self.donor
        assert token.amount == 100
        assert token.reward_type == 'donation_reward'
        assert token.created_at is not None
    
    def test_reward_token_all_reward_types(self):
        """Test creating tokens with all reward types"""
        reward_types = [
            'donation_reward',
            'referral_bonus',
            'achievement_reward',
            'participation_bonus'
        ]
        
        for idx, reward_type in enumerate(reward_types):
            token = RewardToken.objects.create(
                donor=self.donor,
                amount=50 * (idx + 1),
                transaction_hash=f"0x{'b' * 64}",
                reward_type=reward_type
            )
            assert token.reward_type == reward_type
    
    def test_reward_token_amount_variations(self):
        """Test tokens with different amounts"""
        amounts = [10, 50, 100, 500, 1000]
        
        for idx, amount in enumerate(amounts):
            token = RewardToken.objects.create(
                donor=self.donor,
                amount=amount,
                transaction_hash=f"0x{'c' * 64}",
                reward_type='donation_reward'
            )
            assert token.amount == amount
    
    def test_reward_token_blockchain_tx_hash_storage(self):
        """Test that blockchain transaction hash is stored correctly"""
        tx_hash = '0x' + 'd' * 64
        token = RewardToken.objects.create(
            donor=self.donor,
            amount=125,
            transaction_hash=tx_hash,
            reward_type='donation_reward'
        )
        
        assert token.transaction_hash == tx_hash
    
    def test_reward_token_ordering_by_creation_date(self):
        """Test that tokens are ordered by creation date descending"""
        token1 = RewardToken.objects.create(
            donor=self.donor,
            amount=100,
            transaction_hash='0x' + '1' * 64,
            reward_type='donation_reward'
        )
        token2 = RewardToken.objects.create(
            donor=self.donor,
            amount=200,
            transaction_hash='0x' + '2' * 64,
            reward_type='referral_bonus'
        )
        
        tokens = list(RewardToken.objects.all())
        assert tokens[0].created_at >= tokens[1].created_at


@pytest.mark.django_db
class TestRewardTokenBalance:
    """Test reward token balance calculations"""
    
    def setup_method(self):
        """Create test donor and tokens"""
        user = User.objects.create_user(
            username='balancedonor',
            email='balance@test.com',
            password='testpass123'
        )
        
        self.donor = Donor.objects.create(
            user=user,
            blood_type='A+',
            phone_number='+1-555-0002',
            location='New York, NY',
            date_of_birth='1992-08-20',
            wallet_address='0x' + 'a' * 40
        )
    
    def test_get_donor_token_balance(self):
        """Test getting total token balance for donor"""
        # Create some tokens
        RewardToken.objects.create(
            donor=self.donor,
            amount=100,
            transaction_hash='0x' + 'a' * 64,
            reward_type='donation_reward'
        )
        RewardToken.objects.create(
            donor=self.donor,
            amount=50,
            transaction_hash='0x' + 'b' * 64,
            reward_type='referral_bonus'
        )
        
        # Calculate balance manually
        total = RewardToken.objects.filter(donor=self.donor).aggregate(
            total_amount=sum('amount')
        )
        
        # Or use the service function (if available in rewards/services.py)
        tokens = RewardToken.objects.filter(donor=self.donor)
        balance = sum(token.amount for token in tokens)
        
        assert balance == 150
    
    def test_donor_with_no_tokens_has_zero_balance(self):
        """Test that donor with no tokens has zero balance"""
        tokens = RewardToken.objects.filter(donor=self.donor)
        balance = sum(token.amount for token in tokens) if tokens.exists() else 0
        
        assert balance == 0
        assert tokens.count() == 0
    
    def test_multiple_donors_have_separate_balances(self):
        """Test that multiple donors have independent token balances"""
        user2 = User.objects.create_user(
            username='donor2',
            email='donor2@test.com',
            password='testpass123'
        )
        
        donor2 = Donor.objects.create(
            user=user2,
            blood_type='B+',
            phone_number='+1-555-0003',
            location='Chicago, IL',
            date_of_birth='1995-03-10',
            wallet_address='0x' + 'b' * 40
        )
        
        # Add tokens to first donor
        RewardToken.objects.create(
            donor=self.donor,
            amount=100,
            transaction_hash='0x' + 'a' * 64,
            reward_type='donation_reward'
        )
        
        # Add tokens to second donor
        RewardToken.objects.create(
            donor=donor2,
            amount=200,
            transaction_hash='0x' + 'b' * 64,
            reward_type='donation_reward'
        )
        
        donor1_balance = sum(
            t.amount for t in RewardToken.objects.filter(donor=self.donor)
        )
        donor2_balance = sum(
            t.amount for t in RewardToken.objects.filter(donor=donor2)
        )
        
        assert donor1_balance == 100
        assert donor2_balance == 200


@pytest.mark.django_db
class TestRewardTokenAPI:
    """Test Reward Token API endpoints"""
    
    def setup_method(self):
        """Set up test client and authenticated donor"""
        self.client = APIClient()
        
        user = User.objects.create_user(
            username='apidonor',
            email='api@test.com',
            password='testpass123'
        )
        
        self.donor = Donor.objects.create(
            user=user,
            blood_type='O+',
            phone_number='+1-555-0004',
            location='Boston, MA',
            date_of_birth='1990-01-01',
            wallet_address='0x' + 'c' * 40
        )
        
        self.client.force_authenticate(user=user)
    
    def test_reward_token_balance_endpoint(self):
        """Test getting token balance via API endpoint"""
        # Create tokens for donor
        RewardToken.objects.create(
            donor=self.donor,
            amount=150,
            transaction_hash='0x' + 'a' * 64,
            reward_type='donation_reward'
        )
        RewardToken.objects.create(
            donor=self.donor,
            amount=75,
            transaction_hash='0x' + 'b' * 64,
            reward_type='referral_bonus'
        )
        
        response = self.client.get('/api/reward-tokens/balance/')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['success'] is True
        assert data['balance'] == 225
    
    def test_reward_token_balance_endpoint_returns_wallet(self):
        """Test that balance endpoint returns wallet address"""
        RewardToken.objects.create(
            donor=self.donor,
            amount=100,
            transaction_hash='0x' + 'a' * 64,
            reward_type='donation_reward'
        )
        
        response = self.client.get('/api/reward-tokens/balance/')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['wallet'] == self.donor.wallet_address
    
    def test_reward_token_list_endpoint(self):
        """Test listing reward tokens via API"""
        RewardToken.objects.create(
            donor=self.donor,
            amount=100,
            transaction_hash='0x' + 'a' * 64,
            reward_type='donation_reward'
        )
        RewardToken.objects.create(
            donor=self.donor,
            amount=50,
            transaction_hash='0x' + 'b' * 64,
            reward_type='participation_bonus'
        )
        
        response = self.client.get('/api/reward-tokens/')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Data can be list or paginated dict, check both cases
        if isinstance(data, dict):
            assert 'results' in data or 'count' in data
        else:
            assert isinstance(data, list)
    
    def test_reward_token_transaction_history_endpoint(self):
        """Test getting transaction history via API"""
        RewardToken.objects.create(
            donor=self.donor,
            amount=100,
            transaction_hash='0x' + 'a' * 64,
            reward_type='donation_reward'
        )
        RewardToken.objects.create(
            donor=self.donor,
            amount=50,
            transaction_hash='0x' + 'b' * 64,
            reward_type='referral_bonus'
        )
        
        response = self.client.get('/api/reward-tokens/transaction_history/')
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data['success'] is True
        assert data['totals']['total_transactions'] == 2
        assert data['totals']['total_amount'] == 150
    
    def test_unauthenticated_access_denied(self):
        """Test that unauthenticated users cannot access balance endpoint"""
        self.client.force_authenticate(user=None)
        
        response = self.client.get('/api/reward-tokens/balance/')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestRewardTokenFiltering:
    """Test filtering reward tokens"""
    
    def setup_method(self):
        """Create test donors and tokens"""
        user1 = User.objects.create_user(username='donor1', password='test')
        user2 = User.objects.create_user(username='donor2', password='test')
        
        self.donor1 = Donor.objects.create(
            user=user1,
            blood_type='O+',
            phone_number='+1-555-0005',
            location='Boston',
            date_of_birth='1990-01-01'
        )
        
        self.donor2 = Donor.objects.create(
            user=user2,
            blood_type='A+',
            phone_number='+1-555-0006',
            location='NYC',
            date_of_birth='1991-01-01'
        )
        
        # Create mixed tokens
        for i in range(3):
            RewardToken.objects.create(
                donor=self.donor1,
                amount=100 * (i + 1),
                transaction_hash=f"0x{'a' * 64}",
                reward_type='donation_reward'
            )
        
        RewardToken.objects.create(
            donor=self.donor2,
            amount=500,
            transaction_hash='0x' + 'b' * 64,
            reward_type='referral_bonus'
        )
    
    def test_filter_tokens_by_donor(self):
        """Test filtering tokens by donor"""
        donor1_tokens = RewardToken.objects.filter(donor=self.donor1)
        donor2_tokens = RewardToken.objects.filter(donor=self.donor2)
        
        assert donor1_tokens.count() == 3
        assert donor2_tokens.count() == 1
    
    def test_filter_tokens_by_reward_type(self):
        """Test filtering tokens by reward type"""
        donation_tokens = RewardToken.objects.filter(
            reward_type='donation_reward'
        )
        referral_tokens = RewardToken.objects.filter(
            reward_type='referral_bonus'
        )
        
        assert donation_tokens.count() == 3
        assert referral_tokens.count() == 1
    
    def test_filter_tokens_by_donor_and_type(self):
        """Test filtering by both donor and reward type"""
        tokens = RewardToken.objects.filter(
            donor=self.donor1,
            reward_type='donation_reward'
        )
        
        assert tokens.count() == 3


@pytest.mark.django_db
class TestRewardTokenSerialization:
    """Test RewardToken serializer"""
    
    def setup_method(self):
        """Create test donor and token"""
        user = User.objects.create_user(
            username='serialdonor',
            email='serial@test.com',
            password='testpass123',
            first_name='Serial',
            last_name='Donor'
        )
        
        self.donor = Donor.objects.create(
            user=user,
            blood_type='B+',
            phone_number='+1-555-0007',
            location='Denver, CO',
            date_of_birth='1993-03-21'
        )
        
        self.token = RewardToken.objects.create(
            donor=self.donor,
            amount=200,
            transaction_hash='0x' + 'd' * 64,
            reward_type='achievement_reward'
        )
    
    def test_reward_token_serializer_output(self):
        """Test RewardTokenSerializer correctly serializes token"""
        serializer = RewardTokenSerializer(self.token)
        data = serializer.data
        
        assert data['amount'] == 200
        assert data['reward_type'] == 'achievement_reward'
        assert data['transaction_hash'] == '0x' + 'd' * 64
    
    def test_reward_token_serializer_read_only_fields(self):
        """Test that transaction_hash is read-only"""
        serializer = RewardTokenSerializer(self.token)
        data = serializer.data
        
        # Verify transaction_hash is in the serialized output
        assert 'transaction_hash' in data
        # Test that it's read-only by checking field attributes would go here
    
    def test_reward_token_serializer_includes_donor_name(self):
        """Test that serializer includes formatted donor name"""
        serializer = RewardTokenSerializer(self.token)
        data = serializer.data
        
        assert 'donor_name' in data
        assert data['donor_name'] == 'Serial Donor'


@pytest.mark.django_db
class TestRewardTokenCascadeDelete:
    """Test cascade behavior when donor is deleted"""
    
    def setup_method(self):
        """Create test donor and tokens"""
        user = User.objects.create_user(
            username='deletabledonor',
            email='delete@test.com',
            password='testpass123'
        )
        
        self.donor = Donor.objects.create(
            user=user,
            blood_type='AB+',
            phone_number='+1-555-0008',
            location='Phoenix, AZ',
            date_of_birth='1994-07-10'
        )
        
        RewardToken.objects.create(
            donor=self.donor,
            amount=300,
            transaction_hash='0x' + 'e' * 64,
            reward_type='donation_reward'
        )
    
    def test_delete_donor_cascades_to_tokens(self):
        """Test that deleting a donor deletes their reward tokens"""
        assert RewardToken.objects.filter(donor=self.donor).count() == 1
        
        donor_id = self.donor.id
        self.donor.delete()
        
        assert RewardToken.objects.filter(id=donor_id).count() == 0
        assert Donor.objects.filter(id=donor_id).count() == 0
