#!/usr/bin/env node

/**
 * BloodChain Contract CLI
 * Command-line interface for interacting with deployed smart contracts
 */

const hre = require("hardhat");
const fs = require("fs");
const path = require("path");
const readline = require("readline");

class ContractCLI {
  constructor() {
    this.contracts = null;
    this.addresses = null;
    this.signer = null;
  }

  async initialize(network) {
    this.network = network || hre.network.name;

    const deploymentsDir = path.join(__dirname, "deployments");
    const addressesFile = path.join(deploymentsDir, `${this.network}-addresses.json`);

    if (!fs.existsSync(addressesFile)) {
      throw new Error(`No deployment found for network: ${this.network}`);
    }

    this.addresses = JSON.parse(fs.readFileSync(addressesFile, "utf8"));
    const [signer] = await hre.ethers.getSigners();
    this.signer = signer;

    // Load contracts
    const BloodUnit = await hre.ethers.getContractFactory("BloodUnit");
    const RewardToken = await hre.ethers.getContractFactory("RewardToken");

    this.contracts = {
      bloodUnit: BloodUnit.attach(this.addresses.BloodUnit),
      rewardToken: RewardToken.attach(this.addresses.RewardToken),
    };
  }

  // BloodUnit Commands
  async registerBloodUnit(unitId, bloodType, donorWallet) {
    console.log(`Registering blood unit: ${unitId}`);
    const tx = await this.contracts.bloodUnit.registerBloodUnit(
      unitId,
      bloodType,
      donorWallet
    );
    const receipt = await tx.wait();
    console.log(`✓ Registered. Tx: ${receipt.transactionHash}`);
    return receipt;
  }

  async updateBloodUnitStatus(unitId, newStatus) {
    console.log(`Updating status of unit ${unitId} to: ${newStatus}`);
    const tx = await this.contracts.bloodUnit.updateBloodUnitStatus(unitId, newStatus);
    const receipt = await tx.wait();
    console.log(`✓ Updated. Tx: ${receipt.transactionHash}`);
    return receipt;
  }

  async getBloodUnit(unitId) {
    const unit = await this.contracts.bloodUnit.getBloodUnit(unitId);
    return {
      unitId: unit.unitId,
      bloodType: unit.bloodType,
      donorWallet: unit.donorWallet,
      status: unit.status,
      registeredAt: new Date(unit.registeredAt.toNumber() * 1000),
      lastUpdatedAt: new Date(unit.lastUpdatedAt.toNumber() * 1000),
    };
  }

  async getTotalBloodUnits() {
    return await this.contracts.bloodUnit.getTotalUnits();
  }

  // RewardToken Commands
  async issueTokens(donorWallet, amount) {
    const amountWei = hre.ethers.utils.parseEther(amount.toString());
    console.log(`Issuing ${amount} BLD tokens to ${donorWallet}`);
    const tx = await this.contracts.rewardToken.issueTokens(donorWallet, amountWei);
    const receipt = await tx.wait();
    console.log(`✓ Tokens issued. Tx: ${receipt.transactionHash}`);
    return receipt;
  }

  async getTokenBalance(address) {
    const balance = await this.contracts.rewardToken.balanceOf(address);
    return hre.ethers.utils.formatEther(balance);
  }

  async getTotalTokenSupply() {
    const supply = await this.contracts.rewardToken.totalSupply();
    return hre.ethers.utils.formatEther(supply);
  }

  async redeemTokens(amount) {
    const amountWei = hre.ethers.utils.parseEther(amount.toString());
    console.log(`Redeeming ${amount} BLD tokens`);
    const tx = await this.contracts.rewardToken.redeemTokens(amountWei);
    const receipt = await tx.wait();
    console.log(`✓ Tokens redeemed. Tx: ${receipt.transactionHash}`);
    return receipt;
  }

  async getRedemptionStats(address) {
    const [totalRedeemed, count] = await this.contracts.rewardToken.getRedemptionStats(
      address
    );
    return {
      totalRedeemed: hre.ethers.utils.formatEther(totalRedeemed),
      redemptionCount: count.toNumber(),
    };
  }

  // Display Commands
  printContracts() {
    console.log("\n╔══════════════════════════════════════════════════════════╗");
    console.log("║           BloodChain Contract Addresses                 ║");
    console.log("╚══════════════════════════════════════════════════════════╝\n");
    console.log(`Network: ${this.network.toUpperCase()}`);
    console.log(`BloodUnit:  ${this.addresses.BloodUnit}`);
    console.log(`RewardToken: ${this.addresses.RewardToken}`);
    console.log(`Deployer:   ${this.addresses.deployer}\n`);
  }

  printHelp() {
    console.log(`
╔══════════════════════════════════════════════════════════╗
║         BloodChain Smart Contract CLI v1.0              ║
╚══════════════════════════════════════════════════════════╝

BLOOD UNIT COMMANDS:
  register <unitId> <bloodType> <donorAddress>
    Register a new blood unit

  status <unitId> <newStatus>
    Update blood unit status

  get <unitId>
    Get blood unit details

  count
    Get total number of blood units

TOKEN COMMANDS:
  issue <donorAddress> <amount>
    Issue tokens to a donor (amount in BLD)

  balance <address>
    Get token balance of an address

  supply
    Get total token supply

  redeem <amount>
    Redeem tokens (amount in BLD)

  stats <address>
    Get redemption statistics

UTILITY COMMANDS:
  addresses
    Show contract addresses

  help
    Show this help message

  exit
    Exit the CLI

EXAMPLES:
  register UNIT-001 "O+" 0x742d35Cc6634C0532925a3b844Bc9e7595f42e1
  status UNIT-001 "available"
  get UNIT-001
  issue 0x742d35Cc6634C0532925a3b844Bc9e7595f42e1 100
  balance 0x742d35Cc6634C0532925a3b844Bc9e7595f42e1
  redeem 50
`);
  }
}

// Main CLI loop
async function main() {
  const cli = new ContractCLI();

  try {
    const network = process.argv[2] || "hardhat";
    await cli.initialize(network);

    console.log(`\n✓ Connected to ${network} network`);
    console.log(`✓ Signer: ${cli.signer.address}`);
    cli.printContracts();
    cli.printHelp();

    // Interactive mode
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
      prompt: `bloodchain> `,
    });

    rl.prompt();

    rl.on("line", async (line) => {
      const args = line.trim().split(" ");
      const command = args[0]?.toLowerCase();

      try {
        switch (command) {
          // BloodUnit commands
          case "register":
            if (args.length < 4) {
              console.log(
                "Usage: register <unitId> <bloodType> <donorAddress>"
              );
            } else {
              await cli.registerBloodUnit(args[1], args[2], args[3]);
            }
            break;

          case "status":
            if (args.length < 3) {
              console.log("Usage: status <unitId> <newStatus>");
            } else {
              await cli.updateBloodUnitStatus(args[1], args[2]);
            }
            break;

          case "get":
            if (args.length < 2) {
              console.log("Usage: get <unitId>");
            } else {
              const unit = await cli.getBloodUnit(args[1]);
              console.log(JSON.stringify(unit, null, 2));
            }
            break;

          case "count":
            const count = await cli.getTotalBloodUnits();
            console.log(`Total blood units: ${count}`);
            break;

          // Token commands
          case "issue":
            if (args.length < 3) {
              console.log("Usage: issue <donorAddress> <amount>");
            } else {
              await cli.issueTokens(args[1], args[2]);
            }
            break;

          case "balance":
            if (args.length < 2) {
              console.log("Usage: balance <address>");
            } else {
              const balance = await cli.getTokenBalance(args[1]);
              console.log(`Balance: ${balance} BLD`);
            }
            break;

          case "supply":
            const supply = await cli.getTotalTokenSupply();
            console.log(`Total supply: ${supply} BLD`);
            break;

          case "redeem":
            if (args.length < 2) {
              console.log("Usage: redeem <amount>");
            } else {
              await cli.redeemTokens(args[1]);
            }
            break;

          case "stats":
            if (args.length < 2) {
              console.log("Usage: stats <address>");
            } else {
              const stats = await cli.getRedemptionStats(args[1]);
              console.log(JSON.stringify(stats, null, 2));
            }
            break;

          // Utility commands
          case "addresses":
            cli.printContracts();
            break;

          case "help":
            cli.printHelp();
            break;

          case "exit":
          case "quit":
            rl.close();
            process.exit(0);
            break;

          case "":
            // Empty line, just show prompt
            break;

          default:
            if (command) {
              console.log(`Unknown command: ${command}. Type 'help' for usage.`);
            }
        }
      } catch (error) {
        console.error(`❌ Error: ${error.message}`);
      }

      rl.prompt();
    });

    rl.on("close", () => {
      console.log("\nGoodbye!");
      process.exit(0);
    });
  } catch (error) {
    console.error(`❌ Initialization error: ${error.message}`);
    process.exit(1);
  }
}

main().catch(console.error);
