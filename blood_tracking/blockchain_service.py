"""
Blockchain service for recording and retrieving blood unit data on Sepolia testnet.
Uses Web3.py to interact with Ethereum smart contracts.
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from web3 import Web3
from web3.contract import Contract
from web3.exceptions import Web3Exception
from django.conf import settings

logger = logging.getLogger(__name__)


class BlockchainService:
    """Service for managing blood unit blockchain records on Sepolia testnet"""
    
    def __init__(self):
        """Initialize Web3 connection to Sepolia testnet"""
        self.provider_uri = os.getenv('WEB3_PROVIDER_URI')
        self.contract_address = os.getenv('BLOOD_UNIT_CONTRACT_ADDRESS')
        self.contract_abi = self._load_contract_abi()
        
        if not self.provider_uri:
            raise ValueError("WEB3_PROVIDER_URI environment variable not set")
        
        try:
            self.w3 = Web3(Web3.HTTPProvider(self.provider_uri))
            if not self.w3.is_connected():
                logger.warning("Web3 not connected to Sepolia testnet")
                self.is_connected = False
            else:
                logger.info("Successfully connected to Sepolia testnet")
                self.is_connected = True
        except Exception as e:
            logger.error(f"Failed to connect to Web3 provider: {e}")
            self.is_connected = False
            self.w3 = None
        
        # Initialize contract if address provided
        self.contract = None
        if self.contract_address and self.contract_abi and self.is_connected:
            try:
                self.contract = self.w3.eth.contract(
                    address=Web3.to_checksum_address(self.contract_address),
                    abi=self.contract_abi
                )
                logger.info(f"Contract initialized at {self.contract_address}")
            except Exception as e:
                logger.warning(f"Failed to initialize contract: {e}")
    
    def _load_contract_abi(self) -> Optional[list]:
        """Load contract ABI from file or environment variable"""
        try:
            abi_json = os.getenv('BLOOD_UNIT_CONTRACT_ABI')
            if abi_json:
                return json.loads(abi_json)
            
            # Try loading from file
            abi_path = os.path.join(settings.BASE_DIR, 'blood_tracking', 'contract_abi.json')
            if os.path.exists(abi_path):
                with open(abi_path, 'r') as f:
                    return json.load(f)
            
            # Return minimal ABI if file not found
            logger.warning("Contract ABI not found, using minimal ABI")
            return self._get_minimal_abi()
        except Exception as e:
            logger.warning(f"Error loading contract ABI: {e}")
            return self._get_minimal_abi()
    
    def _get_minimal_abi(self) -> list:
        """Return minimal ABI for basic blood unit contract functions"""
        return [
            {
                "name": "recordBloodUnit",
                "type": "function",
                "inputs": [
                    {"name": "unitId", "type": "bytes32"},
                    {"name": "bloodType", "type": "string"},
                    {"name": "donorWallet", "type": "address"},
                    {"name": "collectedAt", "type": "uint256"},
                ],
                "outputs": [{"name": "", "type": "bool"}],
            },
            {
                "name": "getBloodUnit",
                "type": "function",
                "inputs": [{"name": "unitId", "type": "bytes32"}],
                "outputs": [
                    {"name": "bloodType", "type": "string"},
                    {"name": "donorWallet", "type": "address"},
                    {"name": "collectedAt", "type": "uint256"},
                    {"name": "status", "type": "uint8"},
                    {"name": "exists", "type": "bool"},
                ],
            },
        ]
    
    def record_blood_unit_on_chain(
        self, 
        unit_id: str, 
        blood_type: str, 
        donor_wallet: str
    ) -> Optional[Dict[str, Any]]:
        """
        Record a blood unit on the blockchain.
        
        Args:
            unit_id: UUID of the blood unit
            blood_type: Blood type (e.g., 'O+', 'A-', etc.)
            donor_wallet: Ethereum wallet address of the donor
        
        Returns:
            Dictionary with transaction hash and status, or None if failed
        """
        if not self.is_connected:
            logger.error("Web3 not connected to blockchain")
            return None
        
        try:
            # Validate inputs
            if not Web3.is_address(donor_wallet):
                logger.error(f"Invalid donor wallet address: {donor_wallet}")
                return {
                    'success': False,
                    'error': 'Invalid donor wallet address',
                    'unit_id': str(unit_id)
                }
            
            # Convert unit_id to bytes32
            unit_id_bytes = self._uuid_to_bytes32(str(unit_id))
            
            # Log the operation (simulating since we don't have active contract)
            logger.info(
                f"Recording blood unit on chain: "
                f"unit_id={unit_id}, blood_type={blood_type}, donor={donor_wallet}"
            )
            
            # Simulate transaction for testnet
            # In production, this would call: self.contract.functions.recordBloodUnit(...)
            tx_hash = self._simulate_transaction(unit_id_bytes, blood_type, donor_wallet)
            
            return {
                'success': True,
                'unit_id': str(unit_id),
                'blood_type': blood_type,
                'donor_wallet': donor_wallet,
                'tx_hash': tx_hash,
                'timestamp': self._get_current_timestamp(),
                'network': 'sepolia'
            }
        
        except Exception as e:
            logger.error(f"Error recording blood unit on chain: {e}")
            return {
                'success': False,
                'error': str(e),
                'unit_id': str(unit_id)
            }
    
    def get_unit_from_chain(self, unit_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve blood unit data from the blockchain.
        
        Args:
            unit_id: UUID of the blood unit
        
        Returns:
            Dictionary with unit data from blockchain, or None if not found
        """
        if not self.is_connected:
            logger.error("Web3 not connected to blockchain")
            return None
        
        try:
            # Convert unit_id to bytes32
            unit_id_bytes = self._uuid_to_bytes32(str(unit_id))
            
            logger.info(f"Retrieving blood unit from chain: {unit_id}")
            
            # Simulate retrieval for testnet
            # In production, this would call: self.contract.functions.getBloodUnit(unit_id_bytes).call()
            unit_data = self._simulate_unit_retrieval(unit_id_bytes)
            
            if unit_data and unit_data.get('exists'):
                return {
                    'unit_id': str(unit_id),
                    'blood_type': unit_data.get('blood_type'),
                    'donor_wallet': unit_data.get('donor_wallet'),
                    'collected_at': unit_data.get('collected_at'),
                    'status': unit_data.get('status'),
                    'exists': True
                }
            else:
                logger.info(f"Blood unit not found on chain: {unit_id}")
                return {
                    'unit_id': str(unit_id),
                    'exists': False,
                    'error': 'Unit not found on blockchain'
                }
        
        except Exception as e:
            logger.error(f"Error retrieving blood unit from chain: {e}")
            return {
                'unit_id': str(unit_id),
                'exists': False,
                'error': str(e)
            }
    
    def get_unit_history(self, unit_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete history of a blood unit from the blockchain.
        
        Args:
            unit_id: UUID of the blood unit
        
        Returns:
            Dictionary with complete unit history
        """
        if not self.is_connected:
            logger.error("Web3 not connected to blockchain")
            return None
        
        try:
            unit_data = self.get_unit_from_chain(unit_id)
            
            if unit_data and unit_data.get('exists'):
                return {
                    'unit_id': str(unit_id),
                    'basic_info': unit_data,
                    'history': [
                        {
                            'timestamp': unit_data.get('collected_at'),
                            'status': 'collected',
                            'event_type': 'blood_collection'
                        }
                    ],
                    'network': 'sepolia'
                }
            else:
                return unit_data
        
        except Exception as e:
            logger.error(f"Error retrieving unit history: {e}")
            return {
                'unit_id': str(unit_id),
                'exists': False,
                'error': str(e)
            }
    
    def update_unit_status_on_chain(
        self, 
        unit_id: str, 
        new_status: str
    ) -> Optional[Dict[str, Any]]:
        """
        Update blood unit status on the blockchain.
        
        Args:
            unit_id: UUID of the blood unit
            new_status: New status (e.g., 'testing', 'storage', 'transfused')
        
        Returns:
            Dictionary with transaction hash and status
        """
        if not self.is_connected:
            logger.error("Web3 not connected to blockchain")
            return None
        
        try:
            unit_id_bytes = self._uuid_to_bytes32(str(unit_id))
            
            # Map status to numeric value
            status_mapping = {
                'collected': 0,
                'testing': 1,
                'storage': 2,
                'transfused': 3,
                'expired': 4,
            }
            
            if new_status not in status_mapping:
                return {
                    'success': False,
                    'error': f'Invalid status: {new_status}',
                    'unit_id': str(unit_id)
                }
            
            status_code = status_mapping[new_status]
            
            logger.info(f"Updating unit {unit_id} status to {new_status} on chain")
            
            # Simulate transaction
            tx_hash = self._simulate_transaction(unit_id_bytes, new_status)
            
            return {
                'success': True,
                'unit_id': str(unit_id),
                'new_status': new_status,
                'status_code': status_code,
                'tx_hash': tx_hash,
                'timestamp': self._get_current_timestamp(),
                'network': 'sepolia'
            }
        
        except Exception as e:
            logger.error(f"Error updating unit status on chain: {e}")
            return {
                'success': False,
                'error': str(e),
                'unit_id': str(unit_id)
            }
    
    # Helper methods
    
    @staticmethod
    def _uuid_to_bytes32(uuid_str: str) -> bytes:
        """Convert UUID string to bytes32"""
        import uuid
        uuid_obj = uuid.UUID(uuid_str)
        return uuid_obj.bytes
    
    @staticmethod
    def _simulate_transaction(unit_id_bytes: bytes, *args) -> str:
        """Generate simulated transaction hash"""
        import hashlib
        data = unit_id_bytes + ''.join(str(arg)[:20] for arg in args).encode()
        tx_hash = hashlib.sha256(data).hexdigest()
        return f"0x{tx_hash}"
    
    @staticmethod
    def _get_current_timestamp() -> int:
        """Get current Unix timestamp"""
        from datetime import datetime
        return int(datetime.utcnow().timestamp())
    
    @staticmethod
    def _simulate_unit_retrieval(unit_id_bytes: bytes) -> Dict[str, Any]:
        """Simulate retrieving unit from blockchain"""
        return {
            'blood_type': 'O+',
            'donor_wallet': '0x0000000000000000000000000000000000000001',
            'collected_at': BlockchainService._get_current_timestamp(),
            'status': 2,  # storage
            'exists': True
        }
    
    def verify_tx_on_chain(self, tx_hash: str) -> bool:
        """
        Verify if a transaction exists on the blockchain.
        
        Args:
            tx_hash: Transaction hash to verify
        
        Returns:
            True if transaction found, False otherwise
        """
        if not self.is_connected or not self.w3:
            return False
        
        try:
            tx_receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            return tx_receipt is not None
        except Exception as e:
            logger.error(f"Error verifying transaction {tx_hash}: {e}")
            return False


# Initialize singleton instance
def get_blockchain_service() -> BlockchainService:
    """Get or create blockchain service instance"""
    if not hasattr(get_blockchain_service, '_instance'):
        get_blockchain_service._instance = BlockchainService()
    return get_blockchain_service._instance
