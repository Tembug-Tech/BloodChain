const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("BloodUnit Contract", function () {
  let bloodUnit;
  let owner, donorWallet1, donorWallet2;

  beforeEach(async function () {
    [owner, donorWallet1, donorWallet2] = await ethers.getSigners();

    const BloodUnit = await ethers.getContractFactory("BloodUnit");
    bloodUnit = await BloodUnit.deploy();
    await bloodUnit.deployed();
  });

  describe("Registration", function () {
    it("Should register a blood unit correctly", async function () {
      const unitId = "UNIT-001";
      const bloodType = "O+";

      await bloodUnit.registerBloodUnit(unitId, bloodType, donorWallet1.address);

      const unit = await bloodUnit.getBloodUnit(unitId);
      expect(unit.unitId).to.equal(unitId);
      expect(unit.bloodType).to.equal(bloodType);
      expect(unit.donorWallet).to.equal(donorWallet1.address);
      expect(unit.status).to.equal("registered");
    });

    it("Should emit BloodUnitRegistered event", async function () {
      const unitId = "UNIT-002";
      const bloodType = "A-";

      await expect(
        bloodUnit.registerBloodUnit(unitId, bloodType, donorWallet1.address)
      )
        .to.emit(bloodUnit, "BloodUnitRegistered")
        .withArgs(unitId, bloodType, donorWallet1.address, await getBlockTimestamp());
    });

    it("Should reject duplicate unit registration", async function () {
      const unitId = "UNIT-003";
      const bloodType = "B+";

      await bloodUnit.registerBloodUnit(unitId, bloodType, donorWallet1.address);

      await expect(
        bloodUnit.registerBloodUnit(unitId, bloodType, donorWallet2.address)
      ).to.be.revertedWith("Blood unit already exists");
    });

    it("Should only allow owner to register units", async function () {
      const unitId = "UNIT-004";
      const bloodType = "AB-";

      await expect(
        bloodUnit
          .connect(donorWallet1)
          .registerBloodUnit(unitId, bloodType, donorWallet2.address)
      ).to.be.revertedWith("Only owner can call this function");
    });
  });

  describe("Status Updates", function () {
    beforeEach(async function () {
      const unitId = "UNIT-TEST";
      const bloodType = "O+";
      await bloodUnit.registerBloodUnit(unitId, bloodType, donorWallet1.address);
    });

    it("Should update blood unit status", async function () {
      const unitId = "UNIT-TEST";
      const newStatus = "available";

      await bloodUnit.updateBloodUnitStatus(unitId, newStatus);

      const status = await bloodUnit.getBloodUnitStatus(unitId);
      expect(status).to.equal(newStatus);
    });

    it("Should emit BloodUnitStatusUpdated event", async function () {
      const unitId = "UNIT-TEST";
      const newStatus = "quarantine";

      await expect(bloodUnit.updateBloodUnitStatus(unitId, newStatus))
        .to.emit(bloodUnit, "BloodUnitStatusUpdated")
        .withArgs(unitId, "registered", newStatus, await getBlockTimestamp());
    });

    it("Should reject status update for non-existent unit", async function () {
      const unitId = "UNIT-NOT-EXISTS";

      await expect(
        bloodUnit.updateBloodUnitStatus(unitId, "used")
      ).to.be.revertedWith("Blood unit does not exist");
    });
  });

  describe("Query Functions", function () {
    it("Should get blood unit details", async function () {
      const unitId = "UNIT-005";
      const bloodType = "AB+";

      await bloodUnit.registerBloodUnit(unitId, bloodType, donorWallet1.address);

      const unit = await bloodUnit.getBloodUnit(unitId);
      expect(unit.unitId).to.equal(unitId);
      expect(unit.bloodType).to.equal(bloodType);
      expect(unit.donorWallet).to.equal(donorWallet1.address);
    });

    it("Should get blood type for a unit", async function () {
      const unitId = "UNIT-006";
      const bloodType = "B-";

      await bloodUnit.registerBloodUnit(unitId, bloodType, donorWallet1.address);

      const retrievedBloodType = await bloodUnit.getBloodType(unitId);
      expect(retrievedBloodType).to.equal(bloodType);
    });

    it("Should get donor wallet for a unit", async function () {
      const unitId = "UNIT-007";
      const bloodType = "O+";

      await bloodUnit.registerBloodUnit(unitId, bloodType, donorWallet1.address);

      const donor = await bloodUnit.getDonorWallet(unitId);
      expect(donor).to.equal(donorWallet1.address);
    });

    it("Should check if unit exists", async function () {
      const unitId = "UNIT-008";
      const bloodType = "A+";

      expect(await bloodUnit.doesUnitExist(unitId)).to.be.false;

      await bloodUnit.registerBloodUnit(unitId, bloodType, donorWallet1.address);

      expect(await bloodUnit.doesUnitExist(unitId)).to.be.true;
    });

    it("Should get total number of units", async function () {
      const initialCount = await bloodUnit.getTotalUnits();
      expect(initialCount).to.equal(0);

      await bloodUnit.registerBloodUnit("UNIT-009", "O+", donorWallet1.address);
      await bloodUnit.registerBloodUnit("UNIT-010", "A-", donorWallet2.address);

      const finalCount = await bloodUnit.getTotalUnits();
      expect(finalCount).to.equal(2);
    });
  });
});

describe("RewardToken Contract", function () {
  let rewardToken;
  let owner, donor1, donor2, other;

  beforeEach(async function () {
    [owner, donor1, donor2, other] = await ethers.getSigners();

    const RewardToken = await ethers.getContractFactory("RewardToken");
    rewardToken = await RewardToken.deploy();
    await rewardToken.deployed();
  });

  describe("Token Issuance", function () {
    it("Should issue tokens to a donor", async function () {
      const amount = ethers.utils.parseEther("100");

      await rewardToken.issueTokens(donor1.address, amount);

      const balance = await rewardToken.balanceOf(donor1.address);
      expect(balance).to.equal(amount);
    });

    it("Should emit TokensIssued event", async function () {
      const amount = ethers.utils.parseEther("50");

      await expect(rewardToken.issueTokens(donor1.address, amount))
        .to.emit(rewardToken, "TokensIssued")
        .withArgs(owner.address, donor1.address, amount, await getBlockTimestamp());
    });

    it("Should increase total supply", async function () {
      const amount = ethers.utils.parseEther("100");

      const initialSupply = await rewardToken.totalSupply();
      await rewardToken.issueTokens(donor1.address, amount);
      const finalSupply = await rewardToken.totalSupply();

      expect(finalSupply).to.equal(initialSupply.add(amount));
    });

    it("Should only allow authorized issuers", async function () {
      const amount = ethers.utils.parseEther("50");

      await expect(
        rewardToken.connect(other).issueTokens(donor1.address, amount)
      ).to.be.revertedWith("Only owner or authorized issuer can issue tokens");
    });
  });

  describe("Token Redemption", function () {
    beforeEach(async function () {
      const amount = ethers.utils.parseEther("100");
      await rewardToken.issueTokens(donor1.address, amount);
    });

    it("Should redeem tokens", async function () {
      const redeemAmount = ethers.utils.parseEther("50");

      await rewardToken.connect(donor1).redeemTokens(redeemAmount);

      const balance = await rewardToken.balanceOf(donor1.address);
      expect(balance).to.equal(ethers.utils.parseEther("50"));
    });

    it("Should emit TokensRedeemed event", async function () {
      const redeemAmount = ethers.utils.parseEther("30");

      await expect(rewardToken.connect(donor1).redeemTokens(redeemAmount))
        .to.emit(rewardToken, "TokensRedeemed")
        .withArgs(donor1.address, redeemAmount, await getBlockTimestamp());
    });

    it("Should track redemption statistics", async function () {
      const redeemAmount = ethers.utils.parseEther("20");

      await rewardToken.connect(donor1).redeemTokens(redeemAmount);

      const [totalRedeemed, redemptionCount] = await rewardToken.getRedemptionStats(
        donor1.address
      );
      expect(totalRedeemed).to.equal(redeemAmount);
      expect(redemptionCount).to.equal(1);
    });

    it("Should reject redemption with insufficient balance", async function () {
      const redeemAmount = ethers.utils.parseEther("150");

      await expect(
        rewardToken.connect(donor1).redeemTokens(redeemAmount)
      ).to.be.revertedWith("Insufficient token balance");
    });
  });

  describe("ERC-20 Transfer Functions", function () {
    beforeEach(async function () {
      const amount = ethers.utils.parseEther("100");
      await rewardToken.issueTokens(donor1.address, amount);
    });

    it("Should transfer tokens between donors", async function () {
      const transferAmount = ethers.utils.parseEther("30");

      await rewardToken.connect(donor1).transfer(donor2.address, transferAmount);

      expect(await rewardToken.balanceOf(donor1.address)).to.equal(
        ethers.utils.parseEther("70")
      );
      expect(await rewardToken.balanceOf(donor2.address)).to.equal(transferAmount);
    });

    it("Should handle approvals correctly", async function () {
      const approveAmount = ethers.utils.parseEther("50");

      await rewardToken.connect(donor1).approve(donor2.address, approveAmount);

      const allowance = await rewardToken.allowance(donor1.address, donor2.address);
      expect(allowance).to.equal(approveAmount);
    });

    it("Should transfer tokens using transferFrom", async function () {
      const transferAmount = ethers.utils.parseEther("40");

      await rewardToken.connect(donor1).approve(donor2.address, transferAmount);
      await rewardToken
        .connect(donor2)
        .transferFrom(donor1.address, donor2.address, transferAmount);

      expect(await rewardToken.balanceOf(donor1.address)).to.equal(
        ethers.utils.parseEther("60")
      );
      expect(await rewardToken.balanceOf(donor2.address)).to.equal(transferAmount);
    });
  });

  describe("Issuer Management", function () {
    it("Should authorize an issuer", async function () {
      await rewardToken.authorizeIssuer(donor1.address);

      expect(await rewardToken.isAuthorizedIssuer(donor1.address)).to.be.true;
    });

    it("Should allow authorized issuer to issue tokens", async function () {
      const amount = ethers.utils.parseEther("50");

      await rewardToken.authorizeIssuer(donor1.address);
      await rewardToken
        .connect(donor1)
        .issueTokens(donor2.address, amount);

      expect(await rewardToken.balanceOf(donor2.address)).to.equal(amount);
    });

    it("Should revoke issuer authorization", async function () {
      await rewardToken.authorizeIssuer(donor1.address);
      expect(await rewardToken.isAuthorizedIssuer(donor1.address)).to.be.true;

      await rewardToken.revokeIssuer(donor1.address);
      expect(await rewardToken.isAuthorizedIssuer(donor1.address)).to.be.false;
    });

    it("Should not allow revoked issuers to issue tokens", async function () {
      const amount = ethers.utils.parseEther("50");

      await rewardToken.authorizeIssuer(donor1.address);
      await rewardToken.revokeIssuer(donor1.address);

      await expect(
        rewardToken
          .connect(donor1)
          .issueTokens(donor2.address, amount)
      ).to.be.revertedWith("Only owner or authorized issuer can issue tokens");
    });
  });
});

// Helper function to get current block timestamp
async function getBlockTimestamp() {
  const block = await ethers.provider.getBlock("latest");
  return block.timestamp;
}
