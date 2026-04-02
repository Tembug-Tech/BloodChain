// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title BloodUnit
 * @dev Manages blood unit records on the blockchain
 * Allows registration, tracking, and status updates of blood units
 */
contract BloodUnit {
    
    // Struct to store blood unit information
    struct Unit {
        string unitId;
        string bloodType;
        address donorWallet;
        string status;
        uint256 registeredAt;
        uint256 lastUpdatedAt;
    }
    
    // Mapping to store blood units by unitId
    mapping(string => Unit) public bloodUnits;
    
    // Mapping to track all registered unit IDs
    mapping(string => bool) public unitExists;
    
    // Array of all unit IDs for enumeration
    string[] public allUnitIds;
    
    // Contract owner
    address public owner;
    
    // Events
    event BloodUnitRegistered(
        string indexed unitId,
        string bloodType,
        address indexed donorWallet,
        uint256 timestamp
    );
    
    event BloodUnitStatusUpdated(
        string indexed unitId,
        string oldStatus,
        string newStatus,
        uint256 timestamp
    );
    
    event BloodUnitStatusChanged(
        string indexed unitId,
        string newStatus,
        uint256 timestamp
    );
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    modifier unitMustExist(string memory _unitId) {
        require(unitExists[_unitId], "Blood unit does not exist");
        _;
    }
    
    // Constructor
    constructor() {
        owner = msg.sender;
    }
    
    /**
     * @dev Register a new blood unit on the blockchain
     * @param unitId Unique identifier for the blood unit
     * @param bloodType Blood type of the unit (e.g., "O+", "A-", etc.)
     * @param donorWallet Address of the donor
     */
    function registerBloodUnit(
        string memory unitId,
        string memory bloodType,
        address donorWallet
    ) public onlyOwner {
        require(donorWallet != address(0), "Invalid donor wallet address");
        require(bytes(unitId).length > 0, "Unit ID cannot be empty");
        require(bytes(bloodType).length > 0, "Blood type cannot be empty");
        require(!unitExists[unitId], "Blood unit already exists");
        
        // Create and store the blood unit
        Unit memory newUnit = Unit({
            unitId: unitId,
            bloodType: bloodType,
            donorWallet: donorWallet,
            status: "registered",
            registeredAt: block.timestamp,
            lastUpdatedAt: block.timestamp
        });
        
        bloodUnits[unitId] = newUnit;
        unitExists[unitId] = true;
        allUnitIds.push(unitId);
        
        emit BloodUnitRegistered(unitId, bloodType, donorWallet, block.timestamp);
    }
    
    /**
     * @dev Update the status of an existing blood unit
     * @param unitId Unique identifier for the blood unit
     * @param newStatus New status for the blood unit (e.g., "quarantine", "available", "used", "discarded")
     */
    function updateBloodUnitStatus(
        string memory unitId,
        string memory newStatus
    ) public onlyOwner unitMustExist(unitId) {
        require(bytes(newStatus).length > 0, "New status cannot be empty");
        
        Unit storage unit = bloodUnits[unitId];
        string memory oldStatus = unit.status;
        
        unit.status = newStatus;
        unit.lastUpdatedAt = block.timestamp;
        
        emit BloodUnitStatusUpdated(unitId, oldStatus, newStatus, block.timestamp);
        emit BloodUnitStatusChanged(unitId, newStatus, block.timestamp);
    }
    
    /**
     * @dev Get details of a blood unit
     * @param unitId Unique identifier for the blood unit
     * @return Unit details including ID, blood type, donor, and status
     */
    function getBloodUnit(string memory unitId) 
        public 
        view 
        unitMustExist(unitId) 
        returns (Unit memory) 
    {
        return bloodUnits[unitId];
    }
    
    /**
     * @dev Check if a blood unit exists
     * @param unitId Unique identifier for the blood unit
     * @return Boolean indicating existence of the unit
     */
    function doesUnitExist(string memory unitId) public view returns (bool) {
        return unitExists[unitId];
    }
    
    /**
     * @dev Get total number of registered blood units
     * @return Total count of blood units
     */
    function getTotalUnits() public view returns (uint256) {
        return allUnitIds.length;
    }
    
    /**
     * @dev Get blood unit ID at a specific index
     * @param index Index in the allUnitIds array
     * @return Unit ID at the given index
     */
    function getUnitIdByIndex(uint256 index) public view returns (string memory) {
        require(index < allUnitIds.length, "Index out of bounds");
        return allUnitIds[index];
    }
    
    /**
     * @dev Get current status of a blood unit
     * @param unitId Unique identifier for the blood unit
     * @return Current status of the unit
     */
    function getBloodUnitStatus(string memory unitId) 
        public 
        view 
        unitMustExist(unitId) 
        returns (string memory) 
    {
        return bloodUnits[unitId].status;
    }
    
    /**
     * @dev Get blood type of a unit
     * @param unitId Unique identifier for the blood unit
     * @return Blood type of the unit
     */
    function getBloodType(string memory unitId) 
        public 
        view 
        unitMustExist(unitId) 
        returns (string memory) 
    {
        return bloodUnits[unitId].bloodType;
    }
    
    /**
     * @dev Get donor wallet address for a unit
     * @param unitId Unique identifier for the blood unit
     * @return Address of the donor
     */
    function getDonorWallet(string memory unitId) 
        public 
        view 
        unitMustExist(unitId) 
        returns (address) 
    {
        return bloodUnits[unitId].donorWallet;
    }
    
    /**
     * @dev Get registration timestamp of a unit
     * @param unitId Unique identifier for the blood unit
     * @return Timestamp when the unit was registered
     */
    function getRegistrationTime(string memory unitId) 
        public 
        view 
        unitMustExist(unitId) 
        returns (uint256) 
    {
        return bloodUnits[unitId].registeredAt;
    }
    
    /**
     * @dev Transfer ownership of the contract
     * @param newOwner Address of the new owner
     */
    function transferOwnership(address newOwner) public onlyOwner {
        require(newOwner != address(0), "Invalid new owner address");
        owner = newOwner;
    }
}
