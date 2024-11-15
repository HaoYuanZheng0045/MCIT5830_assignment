// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

contract Source is AccessControl {
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    bytes32 public constant WARDEN_ROLE = keccak256("BRIDGE_WARDEN_ROLE");
    mapping(address => bool) public approved;
    address[] public tokens;

    event Deposit(address indexed token, address indexed recipient, uint256 amount);
    event Withdrawal(address indexed token, address indexed recipient, uint256 amount);
    event Registration(address indexed token);

    constructor(address admin) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(ADMIN_ROLE, admin);
        _grantRole(WARDEN_ROLE, admin);
    }

    // 用户存款功能
    function deposit(address _token, address _recipient, uint256 _amount) public {
        require(approved[_token], "Token not registered"); // 检查代币是否已注册
        require(_amount > 0, "Amount must be greater than zero"); // 检查金额是否有效

        // 将代币从用户转移到合约
        ERC20(_token).transferFrom(msg.sender, address(this), _amount);

        // 触发存款事件
        emit Deposit(_token, _recipient, _amount);
    }

    // 提现功能，仅限具有WARDEN_ROLE的角色调用
    function withdraw(address _token, address _recipient, uint256 _amount) public onlyRole(WARDEN_ROLE) {
        require(approved[_token], "Token not registered"); // 检查代币是否已注册
        require(_amount > 0, "Amount must be greater than zero"); // 检查金额是否有效
        require(ERC20(_token).balanceOf(address(this)) >= _amount, "Insufficient balance"); // 检查合约余额是否足够

        // 将代币从合约转移到接收者
        ERC20(_token).transfer(_recipient, _amount);

        // 触发提现事件
        emit Withdrawal(_token, _recipient, _amount);
    }

    // 注册新代币功能，仅限具有ADMIN_ROLE的角色调用
    function registerToken(address _token) public onlyRole(ADMIN_ROLE) {
        require(!approved[_token], "Token already registered"); // 检查代币是否已注册

        // 将代币地址添加到批准列表中
        approved[_token] = true;
        tokens.push(_token);

        // 触发注册事件
        emit Registration(_token);
    }
}


