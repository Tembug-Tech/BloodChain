# BloodChain Smart Contracts

This directory contains the Solidity smart contracts for the BloodChain project. The contracts manage blood unit records and reward token distribution on the Ethereum blockchain.

## Overview

### Contracts

#### 1. **BloodUnit.sol**
A smart contract that stores and manages blood unit records on the blockchain.

**Key Features:**
- Register new blood units with donor information
- Update blood unit status (quarantine, available, used, discarded)
- Retrieve blood unit details
- Emit events for all actions
- Owner-controlled access

**Main Functions:**
```solidity
// Register a new blood unit
function registerBloodUnit(string memory unitId, string memory bloodType, address donorWallet) public

// Update blood unit status
function updateBloodUnitStatus(string memory unitId, string memory newStatus) public

// Get blood unit details
function getBloodUnit(string memory unitId) public view returns (Unit memory)

// Get blood unit status
function getBloodUnitStatus(string memory unitId) public view returns (string memory)

// Get blood type
function getBloodType(string memory unitId) public view returns (string memory)

// Get donor wallet address
function getDonorWallet(string memory unitId) public view returns (address)

// Check if unit exists
function doesUnitExist(string memory unitId) public view returns (bool)

// Get total units count
function getTotalUnits() public view returns (uint256)
```

**Events:**
- `BloodUnitRegistered` - Emitted when a blood unit is registered
- `BloodUnitStatusUpdated` - Emitted when status is updated
- `BloodUnitStatusChanged` - Emitted when status changes

---

#### 2. **RewardToken.sol**
An ERC-20 token contract for rewarding blood donors.

**Token Details:**
- Name: BloodToken
- Symbol: BLD
- Decimals: 18
- Fully ERC-20 compliant

**Key Features:**
- Issue tokens to donors (owner/authorized issuers only)
- Redeem tokens (donors can burn their own tokens)
- Standard ERC-20 transfers and approvals
- Authorized issuer management
- Redemption tracking and statistics

**Main Functions:**
```solidity
// Issue tokens to a donor
function issueTokens(address donorWallet, uint256 amount) public returns (bool)

// Redeem/burn tokens
function redeemTokens(uint256 amount) public returns (bool)

// Standard ERC-20 functions
function transfer(address to, uint256 amount) public returns (bool)
function approve(address spender, uint256 amount) public returns (bool)
function transferFrom(address from, address to, uint256 amount) public returns (bool)

// Authorize an address to issue tokens
function authorizeIssuer(address issuer) public

// Revoke issuer authorization
function revokeIssuer(address issuer) public

// Check if address is authorized issuer
function isAuthorizedIssuer(address issuer) public view returns (bool)

// Get redemption statistics
function getRedemptionStats(address donorWallet) public view returns (uint256, uint256)

// Get maximum redeemable amount
function getMaxRedeemable(address donorWallet) public view returns (uint256)
```

**Events:**
- `TokensIssued` - Emitted when tokens are issued to a donor
- `TokensRedeemed` - Emitted when tokens are redeemed
- `IssuerAuthorized` - Emitted when an issuer is authorized
- `IssuerRevoked` - Emitted when issuer authorization is revoked
- `Transfer` - ERC-20 standard transfer event
- `Approval` - ERC-20 standard approval event

---

## Setup Instructions

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn
- A wallet with testnet ETH on Sepolia (for deployment)

### Installation

1. **Navigate to the blockchain directory:**
   ```bash
   cd blockchain
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Setup environment variables:**
   ```bash
   cp .env.example .env
   ```

4. **Edit `.env` with your configuration:**
   ```
   SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_INFURA_API_KEY
   PRIVATE_KEY=your_wallet_private_key
   ETHERSCAN_API_KEY=your_etherscan_api_key (optional)
   ```

### Compilation

Compile the contracts:
```bash
npm run compile
```

This generates the ABI and bytecode in the `artifacts/` directory.

### Deployment

#### Deploy to Sepolia Testnet:
```bash
npm run deploy:sepolia
```

#### Deploy to Local Hardhat Node:
```bash
# Terminal 1: Start Hardhat node
npm run node

# Terminal 2: Deploy to localhost
npm run deploy:localhost
```

### Testing

Run the test suite:
```bash
npm run test
```

Run tests with gas reporting:
```bash
npm run test:gas
```

Generate coverage report:
```bash
npm run coverage
```

### Verification

After deployment to Sepolia, verify contracts on Etherscan:
```bash
npx hardhat verify --network sepolia <CONTRACT_ADDRESS>
```

## Configuration Details

The `hardhat.config.js` is configured with:

- **Solidity Compiler:** v0.8.19 with optimization enabled
- **Networks:**
  - `sepolia` - Ethereum Sepolia testnet (configured from env variables)
  - `hardhat` - Local test network (default)
  - `localhost` - Local Hardhat node
- **Gas Reporter:** Optional USD gas reporting
- **Etherscan:** Contract verification support

## Security Considerations

1. **Private Keys:** Never commit `.env` files to version control. Use `.env.example` as a template.
2. **Owner Access:** Both contracts have owner-only functions. Store private keys securely.
3. **Authorized Issuers:** Only authorized addresses can issue RewardTokens.
4. **Event Logging:** All critical actions emit events for off-chain monitoring.

## Integration with Django Backend

The deployed contract addresses should be added to your Django `settings.py`:

```python
# settings.py
BLOODUNIT_CONTRACT_ADDRESS = os.getenv('BLOODUNIT_CONTRACT_ADDRESS')
REWARD_TOKEN_CONTRACT_ADDRESS = os.getenv('REWARD_TOKEN_CONTRACT_ADDRESS')
WEB3_PROVIDER_URI = os.getenv('WEB3_PROVIDER_URI')
```

Use these addresses in your Django backend to interact with the contracts via Web3.py.

## Useful Links

- **Ethereum Sepolia Testnet:** https://sepolia.etherscan.io
- **Solidity Documentation:** https://docs.soliditylang.org/
- **Hardhat Documentation:** https://hardhat.org/docs
- **OpenZeppelin Contracts:** https://docs.openzeppelin.com/contracts/

## Troubleshooting

### "Invalid RPC URL" Error
- Check that `SEPOLIA_RPC_URL` is correctly set in `.env`
- Ensure you have a valid Infura or Alchemy API key

### "Insufficient Funds" Error
- Get testnet ETH from Sepolia faucet: https://www.sepoliafaucet.com/
- Ensure your wallet has ETH before deploying

### "Compilation Failed" Error
- Verify Solidity version: `npm run compile`
- Check for syntax errors in contract files

## License

MIT License - See LICENSE file for details

## Support

For issues or questions about the contracts, please open an issue in the main BloodChain repository.
