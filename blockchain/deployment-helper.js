const fs = require("fs");
const path = require("path");

/**
 * Get deployment addresses from the most recent deployment file
 * @param {string} network Network name (sepolia, localhost, hardhat)
 * @returns {object} Deployment addresses and contract info
 */
function getDeploymentAddresses(network = "sepolia") {
  const deploymentsDir = path.join(__dirname, "..", "deployments");
  const addressesFile = path.join(deploymentsDir, `${network}-addresses.json`);

  if (fs.existsSync(addressesFile)) {
    const addresses = JSON.parse(fs.readFileSync(addressesFile, "utf8"));
    return addresses;
  }

  throw new Error(
    `Deployment addresses not found for network: ${network}. Please run deployment script first.`
  );
}

/**
 * Get full deployment information including ABIs
 * @param {string} network Network name (sepolia, localhost, hardhat)
 * @returns {object} Complete deployment information
 */
function getDeploymentInfo(network = "sepolia") {
  const deploymentsDir = path.join(__dirname, "..", "deployments");
  const deploymentFile = path.join(deploymentsDir, `${network}-deployment.json`);

  if (fs.existsSync(deploymentFile)) {
    const info = JSON.parse(fs.readFileSync(deploymentFile, "utf8"));
    return info;
  }

  throw new Error(
    `Deployment information not found for network: ${network}. Please run deployment script first.`
  );
}

/**
 * Save environment variables for Django backend
 * @param {string} network Network name
 * @param {string} outputPath Path to save the variables file
 */
function saveDjangoEnv(network = "sepolia", outputPath = "../.env") {
  try {
    const addresses = getDeploymentAddresses(network);

    const envContent = `# Smart Contract Addresses (Auto-generated from blockchain deployment)
BLOODUNIT_CONTRACT_ADDRESS=${addresses.BloodUnit}
REWARD_TOKEN_CONTRACT_ADDRESS=${addresses.RewardToken}
DEPLOYER_ADDRESS=${addresses.deployer}
BLOCKCHAIN_NETWORK=${network}

# Web3 Configuration
WEB3_PROVIDER_URI=https://${network}.infura.io/v3/YOUR_INFURA_API_KEY
CHAIN_ID=${addresses.chainId}
`;

    const fullPath = path.join(__dirname, outputPath);
    fs.writeFileSync(fullPath, envContent, "utf8");

    console.log(`✓ Django environment variables saved to: ${outputPath}`);
    console.log("\nYou need to add these to your Django .env file:");
    console.log("--------------------------------");
    console.log(envContent);
    console.log("--------------------------------");
  } catch (error) {
    console.error("Error saving Django env:", error.message);
  }
}

/**
 * Print formatted deployment information
 * @param {string} network Network name
 */
function printDeploymentInfo(network = "sepolia") {
  try {
    const info = getDeploymentInfo(network);
    const addresses = info.contracts;

    console.log("\n╔══════════════════════════════════════════════════════════╗");
    console.log("║         BLOODCHAIN SMART CONTRACT DEPLOYMENT           ║");
    console.log("╚══════════════════════════════════════════════════════════╝\n");

    console.log(`Network: ${info.network.toUpperCase()}`);
    console.log(`Chain ID: 11155111 (Sepolia Testnet)`);
    console.log(`Deployer: ${info.deployer}`);
    console.log(`Deployed At: ${new Date(info.deployedAt).toLocaleString()}\n`);

    console.log("📋 CONTRACT ADDRESSES:");
    console.log("─────────────────────────────────────────────────────────\n");

    console.log(`✓ BloodUnit Contract`);
    console.log(`  Address: ${addresses.BloodUnit.address}`);
    console.log(
      `  Explorer: https://sepolia.etherscan.io/address/${addresses.BloodUnit.address}\n`
    );

    console.log(`✓ RewardToken Contract (BloodToken - BLD)`);
    console.log(`  Address: ${addresses.RewardToken.address}`);
    console.log(
      `  Explorer: https://sepolia.etherscan.io/address/${addresses.RewardToken.address}\n`
    );

    console.log("💾 CONTRACT ABIS:");
    console.log("─────────────────────────────────────────────────────────\n");

    console.log("BloodUnit ABI:");
    console.log(
      JSON.stringify(addresses.BloodUnit.abi, null, 2).substring(0, 200) + "...\n"
    );

    console.log("RewardToken ABI:");
    console.log(
      JSON.stringify(addresses.RewardToken.abi, null, 2).substring(0, 200) + "...\n"
    );

    console.log("🔗 INTEGRATION:");
    console.log("─────────────────────────────────────────────────────────\n");
    console.log("Add to your Django settings.py:");
    console.log(`BLOODUNIT_CONTRACT_ADDRESS = "${addresses.BloodUnit.address}"`);
    console.log(
      `REWARD_TOKEN_CONTRACT_ADDRESS = "${addresses.RewardToken.address}"`
    );
    console.log("\n");
  } catch (error) {
    console.error("Error:", error.message);
  }
}

// CLI interface
if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];
  const network = args[1] || "sepolia";

  switch (command) {
    case "addresses":
      try {
        const addresses = getDeploymentAddresses(network);
        console.log(JSON.stringify(addresses, null, 2));
      } catch (error) {
        console.error(error.message);
      }
      break;

    case "info":
      printDeploymentInfo(network);
      break;

    case "django":
      saveDjangoEnv(network, args[2] || "../.env.blockchain");
      break;

    case "verify":
      try {
        const info = getDeploymentInfo(network);
        console.log("✓ Deployment verified successfully!");
        console.log(`Found ${Object.keys(info.contracts).length} contracts`);
      } catch (error) {
        console.error("✗ Deployment verification failed:", error.message);
      }
      break;

    default:
      console.log(`
BloodChain Contract Deployment Helper

Usage: node deployment-helper.js <command> [network] [options]

Commands:
  addresses [network]     - Get contract addresses (default: sepolia)
  info [network]          - Print detailed deployment information
  django [network] [path] - Generate Django environment file
  verify [network]        - Verify deployment is valid

Examples:
  node deployment-helper.js addresses sepolia
  node deployment-helper.js info hardhat
  node deployment-helper.js django sepolia ../.env.blockchain
  node deployment-helper.js verify localhost
`);
  }
}

module.exports = {
  getDeploymentAddresses,
  getDeploymentInfo,
  saveDjangoEnv,
  printDeploymentInfo,
};
