# Quick Start Guide - BloodChain Smart Contracts

## Prerequisites

Before starting, make sure you have:
- Node.js v16+ installed
- npm or yarn package manager
- A wallet with Sepolia testnet ETH (for deployment)
  - Get testnet ETH from: https://www.sepoliafaucet.com/
- Infura or Alchemy API key
  - Sign up: https://infura.io or https://www.alchemy.com

## 5-Minute Setup

### 1. Install Dependencies
```bash
cd blockchain
npm install
```

### 2. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` with your settings:
```
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_API_KEY
PRIVATE_KEY=your_private_key_here
```

⚠️ **Never commit `.env` to version control!**

### 3. Compile Contracts
```bash
npm run compile
```

You should see:
```
✓ 2 contracts compiled successfully
```

### 4. Deploy to Sepolia
```bash
npm run deploy:sepolia
```

Expected output:
```
Deploying contracts with account: 0x...
✓ BloodUnit contract deployed to: 0x...
✓ RewardToken contract deployed to: 0x...
```

### 5. Save Contract Addresses
```bash
node deployment-helper.js info sepolia
```

This will display:
- Contract addresses
- Etherscan links
- Django environment variables

## Testing (Optional)

Run tests locally:
```bash
npm run test
```

Run with gas reporting:
```bash
npm run test:gas
```

## Common Tasks

### Deploy to Local Hardhat Network
```bash
# Terminal 1: Start local node
npm run node

# Terminal 2: Deploy
npm run deploy:localhost
```

### Verify Contracts on Etherscan
```bash
npx hardhat verify --network sepolia <CONTRACT_ADDRESS>
```

### Interact with Contracts
```bash
# Run interaction examples
npx hardhat run scripts/interact.js --network sepolia
```

### Get Deployment Information
```bash
# Show all addresses
node deployment-helper.js addresses sepolia

# Show detailed information
node deployment-helper.js info sepolia

# Generate Django environment file
node deployment-helper.js django sepolia ../.env.blockchain
```

## Integration with Django Backend

1. Get contract addresses:
   ```bash
   node deployment-helper.js addresses sepolia
   ```

2. Add to your Django `.env` or `settings.py`:
   ```python
   BLOODUNIT_CONTRACT_ADDRESS = "0x..."
   REWARD_TOKEN_CONTRACT_ADDRESS = "0x..."
   WEB3_PROVIDER_URI = "https://sepolia.infura.io/v3/YOUR_KEY"
   ```

3. Use in Django backend with Web3.py:
   ```python
   from web3 import Web3
   
   web3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URI))
   
   # Load contract ABI from deployment files
   # Interact with contract using Web3.py
   ```

## Troubleshooting

### "SEPOLIA_RPC_URL not set"
```bash
# Make sure .env file exists and contains:
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_KEY
```

### "Insufficient funds"
- Add ETH to your wallet from Sepolia faucet
- https://www.sepoliafaucet.com/

### "Invalid private key"
- Get private key from MetaMask: Settings → Security & Privacy → Show Private Key
- ⚠️ Never share your private key!

### Compilation errors
```bash
# Clean build and try again
npm run clean
npm run compile
```

## Contract Functions

### BloodUnit.sol
Register a blood unit:
```bash
# Using Etherscan or contract interface
registerBloodUnit(string unitId, string bloodType, address donorWallet)
```

Update status:
```bash
updateBloodUnitStatus(string unitId, string newStatus)
```

Get details:
```bash
getBloodUnit(string unitId)  # Returns all unit data
getBloodUnitStatus(string unitId)  # Returns just status
```

### RewardToken.sol
Issue tokens:
```bash
issueTokens(address donorWallet, uint256 amount)
```

Redeem tokens:
```bash
redeemTokens(uint256 amount)
```

Transfer tokens:
```bash
transfer(address to, uint256 amount)
approve(address spender, uint256 amount)
```

Get balance:
```bash
balanceOf(address account)
totalSupply()
```

## Next Steps

1. ✅ Deploy contracts to Sepolia
2. ✅ Verify contracts on Etherscan
3. ✅ Connect Django backend to contracts
4. ✅ Build user interfaces for contract interaction
5. ✅ Add event monitoring/indexing (optional: use The Graph)

## Useful Resources

- **Solidity Docs:** https://docs.soliditylang.org/
- **Hardhat Guide:** https://hardhat.org/hardhat-runner/docs/getting-started
- **Ethers.js:** https://docs.ethers.org/
- **OpenZeppelin:** https://docs.openzeppelin.com/
- **Sepolia Testnet:** https://sepolia.etherscan.io

## Support

For issues or questions:
1. Check error message carefully
2. Review logs in `hardhat.log`
3. Verify .env configuration
4. Check contract address on Etherscan
5. Open issue in BloodChain repository

## Important Notes

- 🔐 **Security:** Never commit private keys
- 💰 **Testnet Only:** These contracts are deployed to Sepolia testnet
- 📋 **Verification:** Always verify contracts on Etherscan after deployment
- 🔄 **Upgrades:** Plan contract upgrades carefully using proxy patterns
- 📊 **Events:** Monitor contract events for critical operations

Good luck! 🚀
