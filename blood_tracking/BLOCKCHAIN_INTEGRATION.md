# Blockchain Integration Guide

## Overview

BloodChain integrates with the Ethereum Sepolia testnet to record and verify blood unit data on the blockchain. This provides immutable records of blood units, ensuring transparency and enabling donor incentives through token rewards.

---

## Setup

### Environment Configuration

Add these variables to your `.env` file:

```bash
# Ethereum RPC Provider for Sepolia testnet
WEB3_PROVIDER_URI=https://sepolia.infura.io/v3/YOUR_INFURA_KEY
# OR
WEB3_PROVIDER_URI=https://rpc.sepolia.org

# Blood Unit Smart Contract Address (optional, can be deployed later)
BLOOD_UNIT_CONTRACT_ADDRESS=0x...

# Blood Unit Contract ABI (JSON string, optional)
BLOOD_UNIT_CONTRACT_ABI='[...]'
```

### Get Infura API Key

1. Visit https://infura.io
2. Sign up for free account
3. Create new project
4. Select "Sepolia" network
5. Copy RPC URL: `https://sepolia.infura.io/v3/YOUR_PROJECT_ID`

Add to `.env`:
```bash
WEB3_PROVIDER_URI=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
```

### Install Dependencies

```bash
pip install web3
```

The `web3.py` library is already listed in requirements.txt.

---

## Blockchain Service

### Location
`blood_tracking/blockchain_service.py`

### Functions

#### 1. `record_blood_unit_on_chain(unit_id, blood_type, donor_wallet)`

Records a blood unit on the blockchain.

**Parameters:**
- `unit_id` (str): UUID of the blood unit
- `blood_type` (str): Blood type (O+, A-, etc.)
- `donor_wallet` (str): Ethereum address of donor

**Returns:** Dictionary with transaction hash

**Example:**
```python
from blood_tracking.blockchain_service import get_blockchain_service

service = get_blockchain_service()
result = service.record_blood_unit_on_chain(
    unit_id="550e8400-e29b-41d4-a716-446655440000",
    blood_type="O+",
    donor_wallet="0x742d35Cc6634C0532925a3b844Bc9e7595f36bEd"
)

if result['success']:
    print(f"Unit recorded: {result['tx_hash']}")
else:
    print(f"Error: {result['error']}")
```

#### 2. `get_unit_from_chain(unit_id)`

Retrieve blood unit data from the blockchain.

**Parameters:**
- `unit_id` (str): UUID of the blood unit

**Returns:** Dictionary with unit data

**Example:**
```python
service = get_blockchain_service()
unit = service.get_unit_from_chain(
    unit_id="550e8400-e29b-41d4-a716-446655440000"
)

if unit['exists']:
    print(f"Blood type: {unit['blood_type']}")
    print(f"Donor: {unit['donor_wallet']}")
else:
    print("Unit not found on blockchain")
```

#### 3. `get_unit_history(unit_id)`

Get complete history of a blood unit from blockchain.

**Parameters:**
- `unit_id` (str): UUID of the blood unit

**Returns:** Dictionary with complete history

**Example:**
```python
service = get_blockchain_service()
history = service.get_unit_history(
    unit_id="550e8400-e29b-41d4-a716-446655440000"
)

for event in history['history']:
    print(f"{event['timestamp']}: {event['event_type']}")
```

#### 4. `update_unit_status_on_chain(unit_id, new_status)`

Update blood unit status on blockchain.

**Parameters:**
- `unit_id` (str): UUID of the blood unit
- `new_status` (str): New status (collected, testing, storage, transfused, expired)

**Returns:** Dictionary with transaction hash

**Example:**
```python
service = get_blockchain_service()
result = service.update_unit_status_on_chain(
    unit_id="550e8400-e29b-41d4-a716-446655440000",
    new_status="storage"
)

if result['success']:
    print(f"Status updated: {result['tx_hash']}")
```

#### 5. `verify_tx_on_chain(tx_hash)`

Verify if a transaction exists on the blockchain.

**Parameters:**
- `tx_hash` (str): Transaction hash to verify

**Returns:** True if transaction found, False otherwise

**Example:**
```python
service = get_blockchain_service()
is_valid = service.verify_tx_on_chain(
    tx_hash="0x1234567890abcdef..."
)

if is_valid:
    print("Transaction verified on blockchain")
```

---

## API Endpoints

### 1. Register Blood Unit on Blockchain
**POST** `/api/blood-tracking/units/register/`

Register a new blood unit and automatically record on blockchain.

**Authentication:** Required (Token)

**Request Body:**
```json
{
  "donor": 1,
  "blood_type": "O+",
  "collected_at": "2026-04-02T10:30:00Z",
  "expiry_date": "2026-05-02T10:30:00Z",
  "hiv_test": false,
  "hepatitis_test": false
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "unit_id": "550e8400-e29b-41d4-a716-446655440000",
  "donor": 1,
  "blood_type": "O+",
  "status": "collected",
  "blockchain_record": {
    "success": true,
    "unit_id": "550e8400-e29b-41d4-a716-446655440000",
    "blood_type": "O+",
    "donor_wallet": "0x742d35Cc6634C0532925a3b844Bc9e7595f36bEd",
    "tx_hash": "0x...",
    "timestamp": 1712138400,
    "network": "sepolia"
  },
  "created_at": "2026-04-02T10:30:00Z"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/blood-tracking/units/register/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "donor": 1,
    "blood_type": "O+",
    "collected_at": "2026-04-02T10:30:00Z",
    "expiry_date": "2026-05-02T10:30:00Z"
  }'
```

### 2. Get Blockchain History
**GET** `/api/blood-tracking/units/{id}/blockchain_history/`

Get complete blockchain history of a blood unit.

**Authentication:** Required (Token)

**Response (200 OK):**
```json
{
  "unit_id": "550e8400-e29b-41d4-a716-446655440000",
  "blood_type": "O+",
  "donor": {
    "name": "John Doe",
    "wallet": "0x742d35Cc6634C0532925a3b844Bc9e7595f36bEd"
  },
  "blockchain": {
    "unit_id": "550e8400-e29b-41d4-a716-446655440000",
    "basic_info": {
      "unit_id": "550e8400-e29b-41d4-a716-446655440000",
      "blood_type": "O+",
      "donor_wallet": "0x742d35Cc6634C0532925a3b844Bc9e7595f36bEd",
      "collected_at": 1712138400,
      "status": 2,
      "exists": true
    },
    "history": [
      {
        "timestamp": 1712138400,
        "status": "collected",
        "event_type": "blood_collection"
      }
    ],
    "network": "sepolia"
  },
  "local_status_history": [
    {
      "previous_status": "collected",
      "new_status": "testing",
      "timestamp": "2026-04-02T11:00:00Z",
      "notes": "Lab testing initiated"
    }
  ],
  "blockchain_tx_hash": "0x...",
  "tests": {
    "hiv_test": true,
    "hepatitis_test": false
  }
}
```

**Example:**
```bash
curl -X GET http://localhost:8000/api/blood-tracking/units/1/blockchain_history/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### 3. Update Status on Blockchain
**PATCH** `/api/blood-tracking/units/{id}/update_blockchain_status/`

Update blood unit status on both database and blockchain.

**Authentication:** Required (Token)

**Request Body:**
```json
{
  "status": "storage",
  "notes": "Tests passed, ready for storage"
}
```

**Response (200 OK):**
```json
{
  "message": "Blood unit status updated from testing to storage",
  "unit_id": "550e8400-e29b-41d4-a716-446655440000",
  "blockchain_result": {
    "success": true,
    "unit_id": "550e8400-e29b-41d4-a716-446655440000",
    "new_status": "storage",
    "status_code": 2,
    "tx_hash": "0x...",
    "timestamp": 1712138400,
    "network": "sepolia"
  },
  "unit": {
    "id": 1,
    "unit_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "storage",
    "status_history": [
      {
        "previous_status": "testing",
        "new_status": "storage",
        "timestamp": "2026-04-02T12:00:00Z",
        "blockchain_tx_hash": "0x...",
        "notes": "Tests passed, ready for storage"
      }
    ]
  }
}
```

**Example:**
```bash
curl -X PATCH http://localhost:8000/api/blood-tracking/units/1/update_blockchain_status/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "storage",
    "notes": "Tests passed"
  }'
```

### 4. Get Blockchain History (by UUID)
**GET** `/api/blood-tracking/units/lifecycle_history/`

Get lifecycle history of a blood unit by UUID.

**Authentication:** Required (Token)

**Query Parameters:**
- `unit_id` (required): UUID of the blood unit

**Response (200 OK):**
```json
{
  "unit_id": "550e8400-e29b-41d4-a716-446655440000",
  "donor": "John Doe",
  "blood_type": "O+",
  "collected_at": "2026-04-02T10:30:00Z",
  "expiry_date": "2026-05-02T10:30:00Z",
  "lifecycle_history": {
    "initial_status": "collected",
    "current_status": "storage",
    "status_changes": [...],
    "total_changes": 2,
    "days_in_storage": 30,
    "is_expired": false
  },
  "status_transitions": {
    "current_status": "storage",
    "history": [...]
  },
  "tests": {
    "hiv_test": true,
    "hepatitis_test": true
  },
  "blockchain_tx_hash": "0x...",
  "current_hospital": 1,
  "created_at": "2026-04-02T10:30:00Z"
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/blood-tracking/units/lifecycle_history/?unit_id=550e8400-e29b-41d4-a716-446655440000" \
  -H "Authorization: Token YOUR_TOKEN"
```

---

## Smart Contract

### Sepolia Testnet Details
- **Network:** Ethereum Sepolia
- **Chain ID:** 11155111
- **Block Time:** ~12 seconds
- **Faucets:** 
  - https://sepoliafaucet.com
  - https://www.infura.io/faucet/sepolia

### Recommended Contract Architecture

```solidity
pragma solidity ^0.8.0;

contract BloodUnitRegistry {
    struct BloodUnit {
        bytes32 unitId;
        string bloodType;
        address donorWallet;
        uint256 collectedAt;
        uint8 status; // 0=collected, 1=testing, 2=storage, 3=transfused, 4=expired
        bool exists;
    }
    
    mapping(bytes32 => BloodUnit) public units;
    event BloodUnitRecorded(bytes32 unitId, string bloodType, uint256 collectedAt);
    event StatusUpdated(bytes32 unitId, uint8 newStatus, uint256 timestamp);
    
    function recordBloodUnit(
        bytes32 unitId,
        string memory bloodType,
        address donorWallet,
        uint256 collectedAt
    ) public {
        units[unitId] = BloodUnit({
            unitId: unitId,
            bloodType: bloodType,
            donorWallet: donorWallet,
            collectedAt: collectedAt,
            status: 0,
            exists: true
        });
        emit BloodUnitRecorded(unitId, bloodType, collectedAt);
    }
    
    function updateStatus(bytes32 unitId, uint8 newStatus) public {
        require(units[unitId].exists, "Unit not found");
        units[unitId].status = newStatus;
        emit StatusUpdated(unitId, newStatus, block.timestamp);
    }
    
    function getBloodUnit(bytes32 unitId) public view returns (BloodUnit memory) {
        return units[unitId];
    }
}
```

### Deployment Instructions

1. **Set up MetaMask:**
   - Add Sepolia network
   - Get test ETH from faucet

2. **Deploy using Remix:**
   - Go to https://remix.ethereum.org
   - Paste smart contract code
   - Compile and deploy to Sepolia
   - Copy contract address

3. **Configure in Django:**
   - Update `.env` with contract address
   - Update contract ABI in environment or `contract_abi.json`

4. **Update Views:**
   - Enable contract interactions in `blockchain_service.py`
   - Uncomment actual contract calls

---

## Usage Workflow

### Complete Blockchain Integration Flow

```python
from blood_tracking.blockchain_service import get_blockchain_service
from blood_tracking.models import BloodUnit
from donor.models import Donor
from datetime import datetime, timedelta

# 1. Create a blood unit
donor = Donor.objects.get(id=1)
unit = BloodUnit.objects.create(
    donor=donor,
    blood_type='O+',
    collected_at=datetime.now(),
    expiry_date=datetime.now() + timedelta(days=35)
)

# 2. Record on blockchain
service = get_blockchain_service()
result = service.record_blood_unit_on_chain(
    unit_id=str(unit.unit_id),
    blood_type=unit.blood_type,
    donor_wallet=donor.wallet_address
)

if result['success']:
    unit.blockchain_tx_hash = result['tx_hash']
    unit.save()

# 3. Later - get blockchain data
unit_from_chain = service.get_unit_from_chain(str(unit.unit_id))
print(f"Unit on chain: {unit_from_chain}")

# 4. Update status on blockchain
status_result = service.update_unit_status_on_chain(
    unit_id=str(unit.unit_id),
    new_status='storage'
)

# 5. Verify transaction
is_verified = service.verify_tx_on_chain(result['tx_hash'])
print(f"Transaction verified: {is_verified}")
```

---

## Error Handling

### Common Errors

**"WEB3_PROVIDER_URI not set"**
- Solution: Add `WEB3_PROVIDER_URI` to `.env`

**"Web3 not connected to Sepolia testnet"**
- Check RPC provider URL
- Verify Sepolia network is working
- Check internet connection

**"Invalid donor wallet address"**
- Ensure wallet format: `0x` + 40 hex characters
- Validate: `Web3.is_address(wallet)`

**"Unit not found on blockchain"**
- Unit may not have been recorded yet
- Check transaction hash in Etherscan
- Verify unit ID is correct

### Transaction Verification

Check your transactions on Sepolia Etherscan:
```
https://sepolia.etherscan.io/tx/YOUR_TX_HASH
```

---

## Testing

### Test Blockchain Service Locally

```python
# In Django shell
python manage.py shell

from blood_tracking.blockchain_service import get_blockchain_service
from django.conf import settings

service = get_blockchain_service()

# Test connection
if service.is_connected:
    print("✓ Connected to Sepolia testnet")
else:
    print("✗ Failed to connect")

# Test recording (simulated)
result = service.record_blood_unit_on_chain(
    unit_id="550e8400-e29b-41d4-a716-446655440000",
    blood_type="O+",
    donor_wallet="0x742d35Cc6634C0532925a3b844Bc9e7595f36bEd"
)

print(f"Result: {result}")

# Test retrieval
unit = service.get_unit_from_chain("550e8400-e29b-41d4-a716-446655440000")
print(f"Unit: {unit}")
```

### API Testing

```bash
# Get auth token
TOKEN=$(curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' | jq -r '.token')

# Test register endpoint
curl -X POST http://localhost:8000/api/blood-tracking/units/register/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "donor": 1,
    "blood_type": "O+",
    "collected_at": "2026-04-02T10:30:00Z",
    "expiry_date": "2026-05-02T10:30:00Z"
  }' | jq .

# Test blockchain history
curl -X GET http://localhost:8000/api/blood-tracking/units/1/blockchain_history/ \
  -H "Authorization: Token $TOKEN" | jq .
```

---

## Production Deployment

### Before Going Live

1. **Deploy Smart Contract**
   - Thorough testing on testnet
   - Formal code audit recommended
   - Deploy to mainnet or production testnet

2. **Configure Environment**
   - Set `WEB3_PROVIDER_URI` to production RPC
   - Set `BLOOD_UNIT_CONTRACT_ADDRESS`
   - Load contract ABI

3. **Security**
   - Use dedicated blockchain service account
   - Implement rate limiting
   - Monitor gas prices
   - Set up alerts for failed transactions

4. **Monitoring**
   - Track transaction fees
   - Monitor blockchain status
   - Log all blockchain interactions
   - Set up failure notifications

### Gas Cost Estimation

Recording a blood unit on blockchain typically costs:
- **Sepolia testnet:** ~500,000 - 1,000,000 gas (~0.01-0.02 ETH)
- **Ethereum mainnet:** ~500,000 - 1,000,000 gas (~$15-50+ depending on gas price)

---

## Resources

- **Web3.py Documentation:** https://web3py.readthedocs.io/
- **Ethereum Docs:** https://ethereum.org/developers
- **Solidity Docs:** https://docs.soliditylang.org/
- **Sepolia Faucet:** https://sepoliafaucet.com
- **Etherscan Sepolia:** https://sepolia.etherscan.io

---

## Support

For blockchain integration issues:
1. Check logs: `tail -f logs/error.log`
2. Test RPC connection: `curl https://sepolia.infura.io/v3/YOUR_KEY`
3. Verify contract on Etherscan
4. Check Web3.py documentation
5. Review transaction hashes in blockchain explorer

---

**Blockchain Version:** 1.0  
**Network:** Sepolia Testnet  
**Last Updated:** 2026-04-02

For more info, see API_DOCUMENTATION.md
