from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
import json
import os

# 连接到 Avalanche Fuji 测试网
w3 = Web3(Web3.HTTPProvider("https://api.avax-test.network/ext/bc/C/rpc"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# 加载 ABI 文件
with open("NFT.abi") as f:
    abi = json.load(f)

# 合约地址
contract_address = "0x85ac2e065d4526FBeE6a2253389669a12318A412"
contract = w3.eth.contract(address=contract_address, abi=abi)

# 使用私钥创建账户
private_key = "0xa589a20c9e95a2218f4ebb69e564527e1e2f5cb673958d32f93cd0399dee04cf"
account = Account.from_key(private_key)

# 定义地址和nonce（nonce应该是一个32字节的数据）
user_address = account.address
nonce = os.urandom(32)  # 生成一个随机的32字节的nonce

# 调用claim函数
tx = contract.functions.claim(user_address, nonce).buildTransaction({
    'from': account.address,
    'nonce': w3.eth.get_transaction_count(account.address),
    'gas': 2000000,
    'gasPrice': w3.toWei('30', 'gwei')  # 提高 gasPrice 至 30 Gwei
})


# 签署并发送交易
signed_tx = w3.eth.account.sign_transaction(tx, private_key)
tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
print("交易已发送，等待回执...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("交易回执:", tx_receipt)




