from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
from pathlib import Path

# 加载合约信息
contract_info_file = "contract_info.json"

def connectTo(chain):
    if chain == 'avax':
        api_url = "https://api.avax-test.network/ext/bc/C/rpc"  # Avalanche Testnet
    elif chain == 'bsc':
        api_url = "https://data-seed-prebsc-1-s1.binance.org:8545/"  # BNB Testnet
    else:
        raise ValueError("Unsupported chain")

    w3 = Web3(Web3.HTTPProvider(api_url))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3

def getContractInfo(chain):
    with open(contract_info_file, 'r') as f:
        contracts = json.load(f)
    return contracts[chain]

def scanBlocks():
    # 初始化链连接
    source_w3 = connectTo("avax")
    dest_w3 = connectTo("bsc")

    # 加载合约
    source_info = getContractInfo("source")
    dest_info = getContractInfo("destination")

    source_contract = source_w3.eth.contract(
        address=source_info["address"],
        abi=source_info["abi"]
    )
    dest_contract = dest_w3.eth.contract(
        address=dest_info["address"],
        abi=dest_info["abi"]
    )

    # 获取最新区块范围
    source_latest = source_w3.eth.block_number
    dest_latest = dest_w3.eth.block_number

    # 扫描事件
    # 1. 监听 Deposit 事件
    deposit_events = source_contract.events.Deposit.createFilter(
        fromBlock=max(0, source_latest - 5)
    ).get_all_entries()

    for event in deposit_events:
        token = event.args.token
        recipient = event.args.recipient
        amount = event.args.amount
        print(f"Deposit event detected: {token}, {recipient}, {amount}")
        
        # 调用目标链的 wrap() 函数
        dest_contract.functions.wrap(token, recipient, amount).transact({
            "from": dest_w3.eth.default_account
        })

    # 2. 监听 Unwrap 事件
    unwrap_events = dest_contract.events.Unwrap.createFilter(
        fromBlock=max(0, dest_latest - 5)
    ).get_all_entries()

    for event in unwrap_events:
        token = event.args.underlying_token
        recipient = event.args.to
        amount = event.args.amount
        print(f"Unwrap event detected: {token}, {recipient}, {amount}")

        # 调用源链的 withdraw() 函数
        source_contract.functions.withdraw(token, recipient, amount).transact({
            "from": source_w3.eth.default_account
        })

if __name__ == "__main__":
    scanBlocks()

