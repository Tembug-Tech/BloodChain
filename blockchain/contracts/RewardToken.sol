// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title RewardToken
 * @dev An ERC-20 token contract for reward distribution to blood donors
 * Token name: BloodToken
 * Token symbol: BLD
 */

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function approve(address spender, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function totalSupply() external view returns (uint256);
    
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
}

contract RewardToken is IERC20 {
    
    // Token metadata
    string public name = "BloodToken";
    string public symbol = "BLD";
    uint8 public decimals = 18;
    
    // Token supply tracking
    uint256 private _totalSupply;
    
    // Balance and allowance mappings
    mapping(address => uint256) public balanceOf;
    mapping(address => mapping(address => uint256)) public allowance;
    
    // Redemption tracking
    mapping(address => uint256) public totalRedeemed;
    mapping(address => uint256) public redemptionCount;
    
    // Owner and authorized issuers
    address public owner;
    mapping(address => bool) public authorizedIssuers;
    
    // Redemption configuration
    uint256 public redeemableFraction = 100; // Percentage of balance that can be redeemed
    
    // Events
    event TokensIssued(
        address indexed issuer,
        address indexed donorWallet,
        uint256 amount,
        uint256 timestamp
    );
    
    event TokensRedeemed(
        address indexed donorWallet,
        uint256 amount,
        uint256 timestamp
    );
    
    event IssuerAuthorized(address indexed issuer, uint256 timestamp);
    event IssuerRevoked(address indexed issuer, uint256 timestamp);
    event RedeemableFractionUpdated(uint256 newFraction, uint256 timestamp);
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this function");
        _;
    }
    
    modifier onlyAuthorized() {
        require(
            msg.sender == owner || authorizedIssuers[msg.sender],
            "Only owner or authorized issuer can issue tokens"
        );
        _;
    }
    
    // Constructor
    constructor() {
        owner = msg.sender;
        authorizedIssuers[msg.sender] = true;
        _totalSupply = 0;
    }
    
    /**
     * @dev Get the total supply of tokens
     * @return Total number of tokens in circulation
     */
    function totalSupply() public view override returns (uint256) {
        return _totalSupply;
    }
    
    /**
     * @dev Get the balance of a token holder
     * @param account Address to check balance for
     * @return Token balance of the account
     */
    function getBalance(address account) public view returns (uint256) {
        return balanceOf[account];
    }
    
    /**
     * @dev Issue reward tokens to a donor (owner/authorized issuer only)
     * @param donorWallet Address of the donor to receive tokens
     * @param amount Number of tokens to issue (in wei)
     */
    function issueTokens(address donorWallet, uint256 amount) 
        public 
        onlyAuthorized 
        returns (bool) 
    {
        require(donorWallet != address(0), "Invalid donor wallet address");
        require(amount > 0, "Amount must be greater than 0");
        
        // Increase total supply
        _totalSupply += amount;
        
        // Add tokens to donor's balance
        balanceOf[donorWallet] += amount;
        
        emit TokensIssued(msg.sender, donorWallet, amount, block.timestamp);
        emit Transfer(address(0), donorWallet, amount);
        
        return true;
    }
    
    /**
     * @dev Redeem tokens by a donor
     * @param amount Number of tokens to redeem
     */
    function redeemTokens(uint256 amount) public returns (bool) {
        require(amount > 0, "Amount must be greater than 0");
        require(balanceOf[msg.sender] >= amount, "Insufficient token balance");
        
        // Deduct from donor's balance
        balanceOf[msg.sender] -= amount;
        
        // Reduce total supply
        _totalSupply -= amount;
        
        // Update redemption tracking
        totalRedeemed[msg.sender] += amount;
        redemptionCount[msg.sender] += 1;
        
        emit TokensRedeemed(msg.sender, amount, block.timestamp);
        emit Transfer(msg.sender, address(0), amount);
        
        return true;
    }
    
    /**
     * @dev Transfer tokens to another address
     * @param to Recipient address
     * @param amount Number of tokens to transfer
     */
    function transfer(address to, uint256 amount) 
        public 
        override 
        returns (bool) 
    {
        return _transfer(msg.sender, to, amount);
    }
    
    /**
     * @dev Approve tokens for spending by another address
     * @param spender Address authorized to spend tokens
     * @param amount Number of tokens authorized
     */
    function approve(address spender, uint256 amount) 
        public 
        override 
        returns (bool) 
    {
        require(spender != address(0), "Invalid spender address");
        allowance[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
        return true;
    }
    
    /**
     * @dev Transfer tokens on behalf of another address (requires approval)
     * @param from Sender address
     * @param to Recipient address
     * @param amount Number of tokens to transfer
     */
    function transferFrom(address from, address to, uint256 amount) 
        public 
        override 
        returns (bool) 
    {
        require(
            allowance[from][msg.sender] >= amount,
            "Insufficient allowance"
        );
        
        allowance[from][msg.sender] -= amount;
        return _transfer(from, to, amount);
    }
    
    /**
     * @dev Internal transfer function
     * @param from Sender address
     * @param to Recipient address
     * @param amount Number of tokens to transfer
     */
    function _transfer(address from, address to, uint256 amount) 
        internal 
        returns (bool) 
    {
        require(from != address(0), "Invalid from address");
        require(to != address(0), "Invalid to address");
        require(balanceOf[from] >= amount, "Insufficient balance");
        
        balanceOf[from] -= amount;
        balanceOf[to] += amount;
        
        emit Transfer(from, to, amount);
        return true;
    }
    
    /**
     * @dev Authorize an address to issue tokens
     * @param issuer Address to authorize as issuer
     */
    function authorizeIssuer(address issuer) public onlyOwner {
        require(issuer != address(0), "Invalid issuer address");
        require(!authorizedIssuers[issuer], "Issuer already authorized");
        
        authorizedIssuers[issuer] = true;
        emit IssuerAuthorized(issuer, block.timestamp);
    }
    
    /**
     * @dev Revoke issuer authorization
     * @param issuer Address to revoke authorization from
     */
    function revokeIssuer(address issuer) public onlyOwner {
        require(issuer != address(0), "Invalid issuer address");
        require(authorizedIssuers[issuer], "Issuer not authorized");
        require(issuer != owner, "Cannot revoke owner");
        
        authorizedIssuers[issuer] = false;
        emit IssuerRevoked(issuer, block.timestamp);
    }
    
    /**
     * @dev Check if an address is authorized to issue tokens
     * @param issuer Address to check
     * @return Boolean indicating authorization status
     */
    function isAuthorizedIssuer(address issuer) public view returns (bool) {
        return issuer == owner || authorizedIssuers[issuer];
    }
    
    /**
     * @dev Get redemption statistics for a donor
     * @param donorWallet Address of the donor
     * @return Total tokens redeemed and redemption count
     */
    function getRedemptionStats(address donorWallet) 
        public 
        view 
        returns (uint256, uint256) 
    {
        return (totalRedeemed[donorWallet], redemptionCount[donorWallet]);
    }
    
    /**
     * @dev Update the redeemable fraction of tokens
     * @param newFraction New redeemable fraction (e.g., 100 for 100%)
     */
    function setRedeemableFraction(uint256 newFraction) public onlyOwner {
        require(newFraction > 0 && newFraction <= 100, "Fraction must be between 1 and 100");
        redeemableFraction = newFraction;
        emit RedeemableFractionUpdated(newFraction, block.timestamp);
    }
    
    /**
     * @dev Get maximum redeemable amount for a donor
     * @param donorWallet Address of the donor
     * @return Maximum amount that can be redeemed
     */
    function getMaxRedeemable(address donorWallet) public view returns (uint256) {
        return (balanceOf[donorWallet] * redeemableFraction) / 100;
    }
    
    /**
     * @dev Transfer ownership to a new owner
     * @param newOwner Address of the new owner
     */
    function transferOwnership(address newOwner) public onlyOwner {
        require(newOwner != address(0), "Invalid new owner address");
        owner = newOwner;
        authorizedIssuers[newOwner] = true;
    }
    
    /**
     * @dev Burn tokens (remove from circulation)
     * @param amount Number of tokens to burn
     */
    function burn(uint256 amount) public returns (bool) {
        require(amount > 0, "Amount must be greater than 0");
        require(balanceOf[msg.sender] >= amount, "Insufficient balance");
        
        balanceOf[msg.sender] -= amount;
        _totalSupply -= amount;
        
        emit Transfer(msg.sender, address(0), amount);
        return true;
    }
    
    /**
     * @dev Increase allowance for a spender
     * @param spender Address authorized to spend
     * @param addedValue Additional amount to approve
     */
    function increaseAllowance(address spender, uint256 addedValue) 
        public 
        returns (bool) 
    {
        require(spender != address(0), "Invalid spender address");
        allowance[msg.sender][spender] += addedValue;
        emit Approval(msg.sender, spender, allowance[msg.sender][spender]);
        return true;
    }
    
    /**
     * @dev Decrease allowance for a spender
     * @param spender Address authorized to spend
     * @param subtractedValue Amount to decrease approval by
     */
    function decreaseAllowance(address spender, uint256 subtractedValue) 
        public 
        returns (bool) 
    {
        require(spender != address(0), "Invalid spender address");
        require(
            allowance[msg.sender][spender] >= subtractedValue,
            "Decreased allowance below zero"
        );
        allowance[msg.sender][spender] -= subtractedValue;
        emit Approval(msg.sender, spender, allowance[msg.sender][spender]);
        return true;
    }
}
