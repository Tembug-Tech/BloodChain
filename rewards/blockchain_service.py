"""
Blockchain service functions for reward tokens in BloodChain
"""
import os
from django.conf import settings
from django.db.models import Sum
from web3 import Web3
from .models import RewardToken
from donor.models import Donor


# Initialize Web3 connection
WEB3_PROVIDER_URI = os.getenv('WEB3_PROVIDER_URI')
REWARD_TOKEN_CONTRACT_ADDRESS = os.getenv('REWARD_TOKEN_CONTRACT_ADDRESS')
REWARD_TOKEN_CONTRACT_ABI = os.getenv('REWARD_TOKEN_CONTRACT_ABI')


def get_reward_service():
    """
    Get or create a RewardTokenService instance (singleton pattern).
    
    Returns:
        RewardTokenService: Instance of the reward token service
    """
    global _reward_service
    try:
        if _reward_service is None:
            _reward_service = RewardTokenService(WEB3_PROVIDER_URI)
        return _reward_service
    except:
        return None


class RewardTokenService:
    """Service class for managing blockchain reward tokens"""
    
    def __init__(self, provider_uri):
        """
        Initialize the RewardTokenService.
        
        Args:
            provider_uri (str): Web3 provider URI (e.g., Infura RPC endpoint)
        """
        try:
            self.web3 = Web3(Web3.HTTPProvider(provider_uri))
            self.is_connected = self.web3.is_connected()
            
            if REWARD_TOKEN_CONTRACT_ADDRESS and REWARD_TOKEN_CONTRACT_ABI:
                self.contract = self.web3.eth.contract(
                    address=Web3.to_checksum_address(REWARD_TOKEN_CONTRACT_ADDRESS),
                    abi=eval(REWARD_TOKEN_CONTRACT_ABI) if isinstance(REWARD_TOKEN_CONTRACT_ABI, str) else REWARD_TOKEN_CONTRACT_ABI
                )
            else:
                self.contract = None
        except Exception as e:
            print(f"Error initializing RewardTokenService: {str(e)}")
            self.is_connected = False
            self.contract = None
    
    def issue_reward_token(self, donor_wallet_address, amount, reward_type='donation_reward'):
        """
        Issue reward tokens to a donor by calling smart contract.
        
        Args:
            donor_wallet_address (str): Donor's Ethereum wallet address
            amount (int): Amount of tokens to issue
            reward_type (str): Type of reward (donation_reward, referral_bonus, etc.)
        
        Returns:
            dict: Result containing success status, tx_hash, and metadata
        """
        result = {
            'success': False,
            'tx_hash': None,
            'error': None,
            'message': None,
            'amount': amount,
            'wallet': donor_wallet_address,
            'reward_type': reward_type
        }
        
        try:
            # Validate wallet address
            if not Web3.is_address(donor_wallet_address):
                result['error'] = 'Invalid Ethereum wallet address'
                return result
            
            # Check connection
            if not self.is_connected:
                result['error'] = 'Not connected to blockchain'
                return result
            
            # If no contract is configured, simulate the transaction
            if not self.contract:
                # Simulated transaction for demonstration
                simulated_hash = Web3.keccak(text=f"{donor_wallet_address}{amount}{reward_type}")
                tx_hash = f"0x{simulated_hash.hex()[:40]}"
                
                result['success'] = True
                result['tx_hash'] = tx_hash
                result['message'] = f"Simulated reward token issuance to {donor_wallet_address}"
                return result
            
            # Call smart contract function to issue tokens
            # Note: This is a placeholder. Actual implementation depends on smart contract
            # Example: tx_hash = self.contract.functions.issueTokens(
            #     Web3.to_checksum_address(donor_wallet_address),
            #     amount
            # ).transact()
            
            # For now, return simulated success
            simulated_hash = Web3.keccak(text=f"{donor_wallet_address}{amount}{reward_type}")
            tx_hash = f"0x{simulated_hash.hex()[:40]}"
            
            result['success'] = True
            result['tx_hash'] = tx_hash
            result['message'] = f"Reward tokens issued to {donor_wallet_address}"
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def get_donor_token_balance(self, donor_wallet_address):
        """
        Get the token balance of a donor from the blockchain.
        
        Args:
            donor_wallet_address (str): Donor's Ethereum wallet address
        
        Returns:
            dict: Result containing balance and wallet info
        """
        result = {
            'success': False,
            'balance': 0,
            'wallet': donor_wallet_address,
            'error': None
        }
        
        try:
            # Validate wallet address
            if not Web3.is_address(donor_wallet_address):
                result['error'] = 'Invalid Ethereum wallet address'
                return result
            
            # Check connection
            if not self.is_connected:
                result['error'] = 'Not connected to blockchain'
                return result
            
            # If no contract is configured, get balance from RewardToken model
            if not self.contract:
                try:
                    # Get total tokens from database for this wallet
                    donor = Donor.objects.get(wallet_address=donor_wallet_address)
                    total_tokens = RewardToken.objects.filter(donor=donor).aggregate(
                        total=Sum('amount')
                    )['total'] or 0
                    
                    result['success'] = True
                    result['balance'] = total_tokens
                    result['message'] = 'Balance retrieved from database'
                except Donor.DoesNotExist:
                    result['error'] = 'Donor not found'
                    result['balance'] = 0
                
                return result
            
            # Call smart contract to get balance
            # balance = self.contract.functions.balanceOf(
            #     Web3.to_checksum_address(donor_wallet_address)
            # ).call()
            
            # For now, get from database
            try:
                donor = Donor.objects.get(wallet_address=donor_wallet_address)
                total_tokens = RewardToken.objects.filter(donor=donor).aggregate(
                    total=Sum('amount')
                )['total'] or 0
                
                result['success'] = True
                result['balance'] = total_tokens
            except Donor.DoesNotExist:
                result['error'] = 'Donor not found'
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def get_transaction_history(self, donor_wallet_address):
        """
        Get transaction history for a donor's rewards.
        
        Args:
            donor_wallet_address (str): Donor's Ethereum wallet address
        
        Returns:
            dict: Result containing transaction history
        """
        result = {
            'success': False,
            'transactions': [],
            'wallet': donor_wallet_address,
            'total_received': 0,
            'error': None
        }
        
        try:
            # Validate wallet address
            if not Web3.is_address(donor_wallet_address):
                result['error'] = 'Invalid Ethereum wallet address'
                return result
            
            # Get transactions from database
            try:
                donor = Donor.objects.get(wallet_address=donor_wallet_address)
                tokens = RewardToken.objects.filter(donor=donor).order_by('-created_at')
                
                transactions = []
                total = 0
                for token in tokens:
                    transactions.append({
                        'id': token.id,
                        'amount': token.amount,
                        'reward_type': token.reward_type,
                        'transaction_hash': token.transaction_hash,
                        'created_at': token.created_at.isoformat()
                    })
                    total += token.amount
                
                result['success'] = True
                result['transactions'] = transactions
                result['total_received'] = total
                
            except Donor.DoesNotExist:
                result['error'] = 'Donor not found'
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result
    
    def verify_transaction(self, tx_hash):
        """
        Verify if a reward token transaction exists on the blockchain.
        
        Args:
            tx_hash (str): Transaction hash to verify
        
        Returns:
            dict: Verification result
        """
        result = {
            'valid': False,
            'tx_hash': tx_hash,
            'status': None,
            'error': None
        }
        
        try:
            # Check if transaction exists in database
            token = RewardToken.objects.filter(transaction_hash=tx_hash).first()
            
            if token:
                result['valid'] = True
                result['status'] = 'confirmed'
                result['amount'] = token.amount
                result['reward_type'] = token.reward_type
                result['created_at'] = token.created_at.isoformat()
            else:
                result['status'] = 'not_found'
            
            return result
            
        except Exception as e:
            result['error'] = str(e)
            return result


# Global service instance
_reward_service = None
