// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "./BridgeToken.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

contract Destination is AccessControl {
    bytes32 public constant CREATOR_ROLE = keccak256("CREATOR_ROLE");
    bytes32 public constant WARDEN_ROLE = keccak256("WARDEN_ROLE");

    // 映射 underlying token 到 wrapped token
    mapping(address => address) public wrapped_tokens;
    // 映射 wrapped token 到 underlying token
    mapping(address => address) public underlying_tokens;

    event Creation(address indexed underlying_token, address indexed wrapped_token);
    event Wrap(address indexed underlying_token, address indexed wrapped_token, address indexed to, uint256 amount);
    event Unwrap(address indexed underlying_token, address indexed wrapped_token, address frm, address indexed to, uint256 amount);

    constructor(address admin) {
        _setupRole(DEFAULT_ADMIN_ROLE, admin);
        _setupRole(CREATOR_ROLE, admin);
        _setupRole(WARDEN_ROLE, admin);
    }

    // 创建桥接代币
    function createToken(
        address underlying,
        string memory name,
        string memory symbol
    ) external onlyRole(CREATOR_ROLE) returns (address) {
        require(wrapped_tokens[underlying] == address(0), "Token already registered");

        BridgeToken newToken = new BridgeToken(underlying, name, symbol, address(this));
        wrapped_tokens[underlying] = address(newToken);
        underlying_tokens[address(newToken)] = underlying;

        emit Creation(underlying, address(newToken));
        return address(newToken);
    }

    // 包装代币
    function wrap(
        address underlying,
        address recipient,
        uint256 amount
    ) external onlyRole(WARDEN_ROLE) {
        address bridgeToken = wrapped_tokens[underlying];
        require(bridgeToken != address(0), "Token not registered");

        BridgeToken(bridgeToken).mint(recipient, amount);
        emit Wrap(underlying, bridgeToken, recipient, amount);
    }

    // 解封代币
    function unwrap(
        address bridgeToken,
        address recipient,
        uint256 amount
    ) external {
        address underlying = underlying_tokens[bridgeToken];
        require(underlying != address(0), "Token not registered");
        require(BridgeToken(bridgeToken).balanceOf(msg.sender) >= amount, "Insufficient balance");

        BridgeToken(bridgeToken).burnFrom(msg.sender, amount);
        emit Unwrap(underlying, bridgeToken, msg.sender, recipient, amount);
    }
}
