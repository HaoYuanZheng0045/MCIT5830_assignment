import random
import json
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.providers.rpc import HTTPProvider

INFURA_API_KEY = "4eea275f633744c2a75821eb1fbc6194"
INFURA_URL = f"https://mainnet.infura.io/v3/{INFURA_API_KEY}"

def connect_to_bnb():
    BNB_TESTNET_URL = "https://data-seed-prebsc-1-s1.binance.org:8545/"
    w3 = Web3(HTTPProvider(BNB_TESTNET_URL))
    try:
        # 测试连接是否成功
        w3.eth.block_number
    except Exception as e:
        raise Exception("Failed to connect to BNB testnet. Please check the network URL and connection.") from e
    return w3


def connect_with_middleware(contract_json):
    # 修改这里为连接到 BNB 测试网
    w3 = connect_to_bnb()
    # Inject Geth POA middleware for networks like BNB Testnet
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    # Load contract ABI and address from the JSON file
    with open(contract_json, "r") as f:
        contract_data = json.load(f)

    # 获取 bsc 下的 address 和 abi
    contract_address = w3.to_checksum_address(contract_data["bsc"]["address"])
    contract_abi = contract_data["bsc"]["abi"]

    contract = w3.eth.contract(address=contract_address, abi=contract_abi)

    return w3, contract




def is_ordered_block(w3, block_num):
    """
    Takes a block number
    Returns a boolean that tells whether all the transactions in the block are ordered by priority fee

    Before EIP-1559, a block is ordered if and only if all transactions are sorted in decreasing order of the gasPrice field

    After EIP-1559, there are two types of transactions
        *Type 0* The priority fee is tx.gasPrice - block.baseFeePerGas
        *Type 2* The priority fee is min( tx.maxPriorityFeePerGas, tx.maxFeePerGas - block.baseFeePerGas )

    Conveniently, most type 2 transactions set the gasPrice field to be min( tx.maxPriorityFeePerGas + block.baseFeePerGas, tx.maxFeePerGas )
    """
    block = w3.eth.get_block(block_num, full_transactions=True)
    transactions = block["transactions"]
    ordered = True  # Assume ordered until proven otherwise

    if not transactions:
        return True  # No transactions to order

    base_fee = block.get("baseFeePerGas", 0)
    last_priority_fee = float("inf")

    for tx in transactions:
        # Determine transaction type (0 or 2) based on the presence of fee fields
        if "gasPrice" in tx:
            # Type 0 transaction
            priority_fee = tx.gasPrice - base_fee
        elif "maxPriorityFeePerGas" in tx and "maxFeePerGas" in tx:
            # Type 2 transaction
            priority_fee = min(tx.maxPriorityFeePerGas, tx.maxFeePerGas - base_fee)
        else:
            continue

        # Check if the current priority fee is less than or equal to the last one
        if priority_fee > last_priority_fee:
            ordered = False
            break

        last_priority_fee = priority_fee

    return ordered

def get_contract_values(contract, admin_address, owner_address):
    """
    Takes a contract object, and two addresses (as strings) to be used for calling
    the contract to check current on chain values.
    The provided "default_admin_role" is the correctly formatted solidity default
    admin value to use when checking with the contract
    To complete this method you need to make three calls to the contract to get:
      onchain_root: Get and return the merkleRoot from the provided contract
      has_role: Verify that the address "admin_address" has the role "default_admin_role" return True/False
      prime: Call the contract to get and return the prime owned by "owner_address"

    check on available contract functions and transactions on the block explorer at
    https://testnet.bscscan.com/address/0xaA7CAaDA823300D18D3c43f65569a47e78220073
    """
    default_admin_role = contract.functions.DEFAULT_ADMIN_ROLE().call()

    # Get the Merkle Root
    onchain_root = contract.functions.merkleRoot().call()

    # Check if the admin_address has the default admin role
    has_role = contract.functions.hasRole(default_admin_role, admin_address).call()

    # Get the prime owned by owner_address
    prime = contract.functions.getPrimeByOwner(owner_address).call()

    return onchain_root, has_role, prime

"""
This might be useful for testing (main is not run by the grader feel free to change 
this code anyway that is helpful)
"""
if __name__ == "__main__":
    # These are addresses associated with the Merkle contract (check on contract
    # functions and transactions on the block explorer at
    # https://testnet.bscscan.com/address/0xaA7CAaDA823300D18D3c43f65569a47e78220073
    admin_address = "0xAC55e7d73A792fE1A9e051BDF4A010c33962809A"
    owner_address = "0x793A37a85964D96ACD6368777c7C7050F05b11dE"
    contract_file = "contract_info.json"

    eth_w3 = connect_to_eth()
    cont_w3, contract = connect_with_middleware(contract_file)

    latest_block = eth_w3.eth.get_block_number()
    london_hard_fork_block_num = 12965000
    assert latest_block > london_hard_fork_block_num, f"Error: the chain never got past the London Hard Fork"

    n = 5
    for _ in range(n):
        block_num = random.randint(1, london_hard_fork_block_num - 1)
        ordered = is_ordered_block(eth_w3, block_num)
        if ordered:
            print(f"Block {block_num} is ordered")
        else:
            print(f"Block {block_num} is not ordered")

