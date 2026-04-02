const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  
  console.log("Deploying contracts with account:", deployer.address);
  console.log("Account balance:", (await deployer.getBalance()).toString());

  try {
    // Deploy BloodUnit contract
    console.log("\n=== Deploying BloodUnit Contract ===");
    const BloodUnit = await hre.ethers.getContractFactory("BloodUnit");
    const bloodUnit = await BloodUnit.deploy();
    await bloodUnit.deployed();
    console.log("BloodUnit contract deployed to:", bloodUnit.address);

    // Deploy RewardToken contract
    console.log("\n=== Deploying RewardToken Contract ===");
    const RewardToken = await hre.ethers.getContractFactory("RewardToken");
    const rewardToken = await RewardToken.deploy();
    await rewardToken.deployed();
    console.log("RewardToken contract deployed to:", rewardToken.address);

    // Save deployment info to a file
    const deploymentInfo = {
      network: hre.network.name,
      deployedAt: new Date().toISOString(),
      deployer: deployer.address,
      contracts: {
        BloodUnit: {
          address: bloodUnit.address,
          abi: BloodUnit.interface.format("json"),
        },
        RewardToken: {
          address: rewardToken.address,
          abi: RewardToken.interface.format("json"),
        },
      },
    };

    // Create deployments directory if it doesn't exist
    const deploymentsDir = path.join(__dirname, "..", "deployments");
    if (!fs.existsSync(deploymentsDir)) {
      fs.mkdirSync(deploymentsDir, { recursive: true });
    }

    // Save to JSON file
    const filename = path.join(
      deploymentsDir,
      `${hre.network.name}-deployment.json`
    );
    fs.writeFileSync(filename, JSON.stringify(deploymentInfo, null, 2));
    console.log("\nDeployment info saved to:", filename);

    // Also save a simplified version with just addresses
    const addressesFile = path.join(
      deploymentsDir,
      `${hre.network.name}-addresses.json`
    );
    const addresses = {
      BloodUnit: bloodUnit.address,
      RewardToken: rewardToken.address,
      deployer: deployer.address,
      chainId: (await hre.ethers.provider.getNetwork()).chainId,
    };
    fs.writeFileSync(addressesFile, JSON.stringify(addresses, null, 2));
    console.log("Addresses saved to:", addressesFile);

    // Print summary
    console.log("\n=== Deployment Summary ===");
    console.log("Network:", hre.network.name);
    console.log("Deployer:", deployer.address);
    console.log("BloodUnit:", bloodUnit.address);
    console.log("RewardToken:", rewardToken.address);

    // Verify contracts on Etherscan if not on localhost/hardhat
    if (hre.network.name === "sepolia") {
      console.log("\n=== Verifying contracts on Etherscan ===");
      console.log("Note: Verification may take a minute...");
      
      // Wait a bit before verification (Etherscan needs time to index)
      await new Promise(resolve => setTimeout(resolve, 30000));
      
      try {
        await hre.run("verify:verify", {
          address: bloodUnit.address,
          constructorArguments: [],
        });
        console.log("BloodUnit verified successfully");
      } catch (error) {
        console.log("BloodUnit verification failed:", error.message);
      }

      try {
        await hre.run("verify:verify", {
          address: rewardToken.address,
          constructorArguments: [],
        });
        console.log("RewardToken verified successfully");
      } catch (error) {
        console.log("RewardToken verification failed:", error.message);
      }
    }

  } catch (error) {
    console.error("Deployment failed:", error);
    process.exit(1);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
