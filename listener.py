from web3 import Web3
from web3.contract import Contract
from web3.providers.rpc import HTTPProvider
from web3.middleware import geth_poa_middleware # Necessary for POA chains
import json
from datetime import datetime
import pandas as pd

# 定义文件路径
eventfile = 'deposit_logs.csv'

def scanBlocks(chain, start_block, end_block, contract_address):
    """
    chain - string (Either 'bsc' or 'avax')
    start_block - integer first block to scan
    end_block - integer last block to scan
    contract_address - the address of the deployed contract

    This function reads "Deposit" events from the specified contract, 
    and writes information about the events to the file "deposit_logs.csv"
    """
    # 根据不同链的类型选择 RPC 端点
    if chain == 'avax':
        api_url = "https://api.avax-test.network/ext/bc/C/rpc"  # AVAX C-chain testnet
    elif chain == 'bsc':
        api_url = "https://data-seed-prebsc-1-s1.binance.org:8545/"  # BSC testnet
    else:
        raise ValueError("Unsupported chain. Use 'avax' or 'bsc'.")

    # 连接到区块链
    w3 = Web3(Web3.HTTPProvider(api_url))

    # 对于 POA 链，注入中间件以确保兼容性
    if chain in ['avax', 'bsc']:
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    # 定义 Deposit 事件的 ABI
    DEPOSIT_ABI = json.loads('[ { "anonymous": false, "inputs": [ { "indexed": true, "internalType": "address", "name": "token", "type": "address" }, { "indexed": true, "internalType": "address", "name": "recipient", "type": "address" }, { "indexed": false, "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "Deposit", "type": "event" }]')

    # 创建合约对象
    contract = w3.eth.contract(address=contract_address, abi=DEPOSIT_ABI)

    # 检查 start_block 和 end_block
    if start_block == "latest":
        start_block = w3.eth.get_block_number()
    if end_block == "latest":
        end_block = w3.eth.get_block_number()

    # 检查区块范围是否合法
    if end_block < start_block:
        print(f"Error: end_block < start_block!")
        return

    print(f"Scanning blocks from {start_block} to {end_block} on {chain}")

    # 事件日志存储列表
    logs = []

    # 如果区块范围小于30，直接获取事件
    if end_block - start_block < 30:
        event_filter = contract.events.Deposit.createFilter(fromBlock=start_block, toBlock=end_block)
        events = event_filter.get_all_entries()

        # 处理事件
        for evt in events:
            token = evt.args['token']
            recipient = evt.args['recipient']
            amount = evt.args['amount']
            transaction_hash = evt.transactionHash.hex()
            contract_address = evt.address

            # 获取事件所在区块的时间戳
            timestamp = datetime.utcfromtimestamp(w3.eth.getBlock(evt.blockNumber)['timestamp'])
            formatted_time = timestamp.strftime('%m/%d/%Y %H:%M:%S')

            logs.append([chain, token, recipient, amount, transaction_hash, contract_address, formatted_time])

    else:
        # 如果区块范围大于30，按区块逐一扫描
        for block_num in range(start_block, end_block + 1):
            event_filter = contract.events.Deposit.createFilter(fromBlock=block_num, toBlock=block_num)
            events = event_filter.get_all_entries()

            for evt in events:
                token = evt.args['token']
                recipient = evt.args['recipient']
                amount = evt.args['amount']
                transaction_hash = evt.transactionHash.hex()
                contract_address = evt.address

                # 获取事件所在区块的时间戳
                timestamp = datetime.utcfromtimestamp(w3.eth.getBlock(evt.blockNumber)['timestamp'])
                formatted_time = timestamp.strftime('%m/%d/%Y %H:%M:%S')

                logs.append([chain, token, recipient, amount, transaction_hash, contract_address, formatted_time])

    # 将数据写入 CSV 文件
    df = pd.DataFrame(logs, columns=['chain', 'token', 'recipient', 'amount', 'transactionHash', 'address', 'date'])

    # 将数据追加到 CSV 文件中，若文件不存在则创建
    df.to_csv(eventfile, mode='a', header=not bool(pd.io.common.get_file_contents(eventfile)), index=False)

    print(f"Logs written to {eventfile}")
