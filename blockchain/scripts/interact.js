const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

/**
 * Load contract ABIs and addresses
 */
async function loadContracts(network) {
  const deploymentsDir = path.join(__dirname, "deployments");
  const addressesFile = path.join(deploymentsDir, `${network}-addresses.json`);
  const deploymentFile = path.join(deploymentsDir, `${network}-deployment.json`);

  if (!fs.existsSync(addressesFile) || !fs.existsSync(deploymentFile)) {
    throw new Error(`Deployment files not found for network: ${network}`);
  }

  const addresses = JSON.parse(fs.readFileSync(addressesFile, "utf8"));
  const deployment = JSON.parse(fs.readFileSync(deploymentFile, "utf8"));

  return { addresses, deployment };
}

/**
 * Get contract instances
 */
async function getContracts() {
  const network = hre.network.name;
  const { addresses, deployment } = await loadContracts(network);

  const BloodUnitFactory = await hre.ethers.getContractFactory("BloodUnit");
  const RewardTokenFactory = await hre.ethers.getContractFactory("RewardToken");

  const bloodUnit = BloodUnitFactory.attach(addresses.BloodUnit);
  const rewardToken = RewardTokenFactory.attach(addresses.RewardToken);

  return { bloodUnit, rewardToken, addresses };
}

// Example interactions
async function main() {
  const [signer] = await hre.ethers.getSigners();
  console.log(`Connected with account: ${signer.address}`);
  console.log(`Network: ${hre.network.name}`);

  try {
    const { bloodUnit, rewardToken, addresses } = await getContracts();

    // Example 1: Register a blood unit
    console.log("\n=== Registering Blood Unit ===");
    const unitId = `UNIT-${Date.now()}`;
    const bloodType = "O+";
    const donorAddress = signer.address;

    const tx1 = await bloodUnit.registerBloodUnit(unitId, bloodType, donorAddress);
    await tx1.wait();
    console.log(`✓ Registered unit: ${unitId}`);

    // Example 2: Get blood unit details
    console.log("\n=== Getting Blood Unit Details ===");
    const unit = await bloodUnit.getBloodUnit(unitId);
    console.log(`Unit ID: ${unit.unitId}`);
    console.log(`Blood Type: ${unit.bloodType}`);
    console.log(`Donor: ${unit.donorWallet}`);
    console.log(`Status: ${unit.status}`);

    // Example 3: Update blood unit status
    console.log("\n=== Updating Blood Unit Status ===");
    const newStatus = "available";
    const tx2 = await bloodUnit.updateBloodUnitStatus(unitId, newStatus);
    await tx2.wait();
    console.log(`✓ Updated status to: ${newStatus}`);

    // Example 4: Issue reward tokens
    console.log("\n=== Issuing Reward Tokens ===");
    const tokenAmount = hre.ethers.utils.parseEther("100");
    const tx3 = await rewardToken.issueTokens(donorAddress, tokenAmount);
    await tx3.wait();
    console.log(`✓ Issued 100 BLD tokens to ${donorAddress}`);

    // Example 5: Get token balance
    console.log("\n=== Checking Token Balance ===");
    const balance = await rewardToken.balanceOf(donorAddress);
    const balanceInBLD = hre.ethers.utils.formatEther(balance);
    console.log(`Balance: ${balanceInBLD} BLD`);

    // Example 6: Redeem tokens
    console.log("\n=== Redeeming Tokens ===");
    const redeemAmount = hre.ethers.utils.parseEther("25");
    const tx4 = await rewardToken.redeemTokens(redeemAmount);
    await tx4.wait();
    console.log(`✓ Redeemed 25 BLD tokens`);

    // Example 7: Get redemption statistics
    console.log("\n=== Redemption Statistics ===");
    const [totalRedeemed, redemptionCount] = await rewardToken.getRedemptionStats(
      donorAddress
    );
    console.log(`Total Redeemed: ${hre.ethers.utils.formatEther(totalRedeemed)} BLD`);
    console.log(`Redemption Count: ${redemptionCount}`);

    // Example 8: Get total blood units
    console.log("\n=== Blood Unit Statistics ===");
    const totalUnits = await bloodUnit.getTotalUnits();
    console.log(`Total Units Registered: ${totalUnits}`);

    // Example 9: Get total token supply
    console.log("\n=== Token Statistics ===");
    const totalSupply = await rewardToken.totalSupply();
    console.log(`Total Token Supply: ${hre.ethers.utils.formatEther(totalSupply)} BLD`);

    console.log("\n✅ Interaction examples completed successfully!");
  } catch (error) {
    console.error("❌ Error:", error);
    process.exit(1);
  }
}

main();

module.exports = { getContracts, loadContracts };
