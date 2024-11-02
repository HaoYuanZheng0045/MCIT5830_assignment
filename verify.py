from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account.messages import encode_defunct
import random
import os

# 连接到 Avalanche Fuji 测试网
w3 = Web3(Web3.HTTPProvider("https://api.avax-test.network/ext/bc/C/rpc"))

# 添加 POA 中间件
w3.middleware_stack.inject(geth_poa_middleware, layer=0)

# 合约地址和 ABI（请使用实际 ABI）
contract_address = "0x85ac2e065d4526FBeE6a2253389669a12318A412"
contract_abi = [...]  # 请替换为合约的实际 ABI

# 连接合约
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

def mintNFT():
    # 使用直接在代码中定义的私钥
    private_key = "0xa589a20c9e95a2218f4ebb69e564527e1e2f5cb673958d32f93cd0399dee04cf"
    account = w3.eth.account.privateKeyToAccount(private_key)

    # 铸造 NFT（以 claim 为例）
    nonce = w3.eth.get_transaction_count(account.address)
    message_nonce = str(random.randint(1, 1000000))  # 生成随机数作为 nonce
    token_id = w3.keccak(text=message_nonce).hex()  # 根据随机数生成 tokenId

    # 构建交易
    txn = contract.functions.claim(message_nonce).buildTransaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 200000,
        'gasPrice': w3.toWei('50', 'gwei')
    })

    # 签名并发送交易
    signed_txn = w3.eth.account.sign_transaction(txn, private_key)
    txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f"Transaction sent with hash: {txn_hash.hex()}")

if __name__ == '__main__':
    # 运行铸造 NFT 的功能
    mintNFT()

