// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/access/AccessControl.sol"; //This allows role-based access control through _grantRole() and the modifier onlyRole
import "@openzeppelin/contracts/token/ERC20/ERC20.sol"; //This contract needs to interact with ERC20 tokens

contract AMM is AccessControl {
    bytes32 public constant LP_ROLE = keccak256("LP_ROLE");
    uint256 public invariant;
    address public tokenA;
    address public tokenB;
    uint256 feebps = 3; // The fee in basis points (i.e., the fee should be feebps/10000)

    event Swap(address indexed _inToken, address indexed _outToken, uint256 inAmt, uint256 outAmt);
    event LiquidityProvision(address indexed _from, uint256 AQty, uint256 BQty);
    event Withdrawal(address indexed _from, address indexed recipient, uint256 AQty, uint256 BQty);

    /*
        Constructor sets the addresses of the two tokens
    */
    constructor(address _tokenA, address _tokenB) {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(LP_ROLE, msg.sender);

        require(_tokenA != address(0), 'Token address cannot be 0');
        require(_tokenB != address(0), 'Token address cannot be 0');
        require(_tokenA != _tokenB, 'Tokens cannot be the same');
        tokenA = _tokenA;
        tokenB = _tokenB;
    }

    function getTokenAddress(uint256 index) public view returns (address) {
        require(index < 2, 'Only two tokens');
        if (index == 0) {
            return tokenA;
        } else {
            return tokenB;
        }
    }

    /*
        Trade function where the user provides sellToken and sellAmount
        Calculate buyAmount using the Uniswap invariant formula and apply fee
    */
    function tradeTokens(address sellToken, uint256 sellAmount) public {
        require(invariant > 0, 'Invariant must be nonzero');
        require(sellToken == tokenA || sellToken == tokenB, 'Invalid token');
        require(sellAmount > 0, 'Cannot trade 0');

        address buyToken = sellToken == tokenA ? tokenB : tokenA;
        uint256 sellReserve = ERC20(sellToken).balanceOf(address(this));
        uint256 buyReserve = ERC20(buyToken).balanceOf(address(this));

        // Calculate effective sell amount after applying fee
        uint256 effectiveSellAmount = (sellAmount * (10000 - feebps)) / 10000;

        // Calculate the amount of buyToken using the Uniswap formula
        uint256 buyAmount = (effectiveSellAmount * buyReserve) / (sellReserve + effectiveSellAmount);

        // Transfer sellToken from the user to the contract
        ERC20(sellToken).transferFrom(msg.sender, address(this), sellAmount);

        // Transfer buyToken from the contract to the user
        ERC20(buyToken).transfer(msg.sender, buyAmount);

        // Update the invariant
        uint256 new_invariant = ERC20(tokenA).balanceOf(address(this)) * ERC20(tokenB).balanceOf(address(this));
        require(new_invariant >= invariant, 'Bad trade');
        invariant = new_invariant;

        emit Swap(sellToken, buyToken, sellAmount, buyAmount);
    }

    /*
        Provide liquidity by pulling amtA of tokenA and amtB of tokenB from the sender
    */
    function provideLiquidity(uint256 amtA, uint256 amtB) public {
        require(amtA > 0 || amtB > 0, 'Cannot provide 0 liquidity');

        // Transfer amtA of tokenA and amtB of tokenB from the sender to the contract
        ERC20(tokenA).transferFrom(msg.sender, address(this), amtA);
        ERC20(tokenB).transferFrom(msg.sender, address(this), amtB);

        // Update the invariant for the first time or recalculated after adding liquidity
        if (invariant == 0) {
            invariant = amtA * amtB;
        } else {
            invariant = ERC20(tokenA).balanceOf(address(this)) * ERC20(tokenB).balanceOf(address(this));
        }

        emit LiquidityProvision(msg.sender, amtA, amtB);
    }

    /*
        Withdraw liquidity: send amtA of tokenA and amtB of tokenB to the recipient
        Only callable by the liquidity provider
    */
    function withdrawLiquidity(address recipient, uint256 amtA, uint256 amtB) public onlyRole(LP_ROLE) {
        require(amtA > 0 || amtB > 0, 'Cannot withdraw 0');
        require(recipient != address(0), 'Cannot withdraw to 0 address');
        
        if (amtA > 0) {
            ERC20(tokenA).transfer(recipient, amtA);
        }
        if (amtB > 0) {
            ERC20(tokenB).transfer(recipient, amtB);
        }
        
        // Recalculate the invariant after withdrawal
        invariant = ERC20(tokenA).balanceOf(address(this)) * ERC20(tokenB).balanceOf(address(this));

        emit Withdrawal(msg.sender, recipient, amtA, amtB);
    }
}
