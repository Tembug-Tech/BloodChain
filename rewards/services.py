"""
Service layer for rewards functionality
"""
from django.db import models
from django.db.models import Sum
from .models import RewardToken
from .blockchain_service import RewardTokenService
import os


def issue_reward_token(donor_wallet_address, amount, reward_type='donation_reward', donor=None):
    """
    Issue reward tokens to a donor via blockchain.
    
    Args:
        donor_wallet_address (str): Ethereum wallet address of donor
        amount (int): Number of tokens to issue
        reward_type (str): Type of reward (donation_reward, referral_bonus, achievement_reward, participation_bonus)
        donor: Donor object (optional, will be looked up if not provided)
    
    Returns:
        dict: Result containing success status and transaction details
    """
    result = {
        'success': False,
        'reward_token': None,
        'tx_hash': None,
        'error': None,
        'message': None
    }
    
    try:
        # Import here to avoid circular imports
        from donor.models import Donor
        
        # Get donor if not provided
        if donor is None:
            try:
                donor = Donor.objects.get(wallet_address=donor_wallet_address)
            except Donor.DoesNotExist:
                result['error'] = f"Donor with wallet {donor_wallet_address} not found"
                return result
        
        # Initialize blockchain service
        web3_provider = os.getenv('WEB3_PROVIDER_URI')
        if not web3_provider:
            result['error'] = 'WEB3_PROVIDER_URI environment variable not configured'
            return result
        
        service = RewardTokenService(web3_provider)
        
        # Check blockchain connection
        if not service.is_connected:
            result['error'] = 'Unable to connect to blockchain'
            return result
        
        # Issue tokens on blockchain
        blockchain_result = service.issue_reward_token(donor_wallet_address, amount, reward_type)
        
        if not blockchain_result.get('success'):
            result['error'] = blockchain_result.get('error', 'Failed to issue tokens on blockchain')
            return result
        
        # Create reward token record in database
        tx_hash = blockchain_result.get('tx_hash')
        reward_token = RewardToken.objects.create(
            donor=donor,
            amount=amount,
            transaction_hash=tx_hash,
            reward_type=reward_type
        )
        
        result['success'] = True
        result['reward_token'] = reward_token
        result['tx_hash'] = tx_hash
        result['message'] = f"Successfully issued {amount} tokens to {donor_wallet_address}"
        
        return result
        
    except Exception as e:
        result['error'] = str(e)
        return result


def get_donor_reward_balance(user):
    """
    Get the total reward token balance for a user's donor profile.
    
    Args:
        user: Django User object
    
    Returns:
        dict: Result containing balance and donor info
    """
    result = {
        'success': False,
        'balance': 0,
        'donor': None,
        'error': None
    }
    
    try:
        from donor.models import Donor
        
        # Get donor for this user
        donor = Donor.objects.get(user=user)
        
        # Calculate total tokens
        total = RewardToken.objects.filter(donor=donor).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        result['success'] = True
        result['balance'] = total
        result['donor'] = donor
        
        return result
        
    except Exception as e:
        result['error'] = str(e)
        return result


def get_reward_transaction_history(user, limit=50):
    """
    Get reward token transaction history for a user.
    
    Args:
        user: Django User object
        limit: Maximum number of transactions to return
    
    Returns:
        dict: Result containing transaction list
    """
    result = {
        'success': False,
        'transactions': [],
        'total_count': 0,
        'total_amount': 0,
        'error': None
    }
    
    try:
        from donor.models import Donor
        
        # Get donor for this user
        donor = Donor.objects.get(user=user)
        
        # Get recent transactions
        tokens = RewardToken.objects.filter(donor=donor).order_by('-created_at')[:limit]
        
        transactions = []
        total_amount = 0
        
        for token in tokens:
            transactions.append({
                'id': token.id,
                'amount': token.amount,
                'reward_type': token.reward_type,
                'transaction_hash': token.transaction_hash,
                'created_at': token.created_at.isoformat(),
                'get_reward_type_display': token.get_reward_type_display()
            })
            total_amount += token.amount
        
        result['success'] = True
        result['transactions'] = transactions
        result['total_count'] = len(transactions)
        result['total_amount'] = total_amount
        
        return result
        
    except Exception as e:
        result['error'] = str(e)
        return result


def get_reward_statistics(user):
    """
    Get comprehensive reward statistics for a donor.
    
    Args:
        user: Django User object
    
    Returns:
        dict: Statistics including balance, count by type, and streaks
    """
    result = {
        'success': False,
        'total_balance': 0,
        'total_rewards': 0,
        'rewards_by_type': {},
        'error': None
    }
    
    try:
        from donor.models import Donor
        
        # Get donor for this user
        donor = Donor.objects.get(user=user)
        
        # Get all tokens
        tokens = RewardToken.objects.filter(donor=donor)
        
        # Calculate totals
        total_balance = 0
        rewards_by_type = {}
        
        for token in tokens:
            total_balance += token.amount
            reward_type = token.get_reward_type_display()
            
            if reward_type not in rewards_by_type:
                rewards_by_type[reward_type] = {'count': 0, 'amount': 0}
            
            rewards_by_type[reward_type]['count'] += 1
            rewards_by_type[reward_type]['amount'] += token.amount
        
        result['success'] = True
        result['total_balance'] = total_balance
        result['total_rewards'] = len(tokens)
        result['rewards_by_type'] = rewards_by_type
        
        return result
        
    except Exception as e:
        result['error'] = str(e)
        return result
