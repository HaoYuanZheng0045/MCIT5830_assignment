from web3 import Web3
from eth_account.messages import encode_defunct
import random

# 连接到 Avalanche 测试网络
w3 = Web3(Web3.HTTPProvider("https://api.avax-test.network/ext/bc/C/rpc"))

# 创建或导入账户
private_key = "0xa589a20c9e95a2218f4ebb69e564527e1e2f5cb673958d32f93cd0399dee04cf"
account = w3.eth.account.from_key(private_key)

# 合约地址和 ABI
contract_address = "0x85ac2e065d4526FBeE6a2253389669a12318A412"
contract_abi = [
    # 这里填入您上传的合约 ABI
    {
        "inputs": [
            {"internalType": "string", "name": "_name", "type": "string"},
            {"internalType": "string", "name": "_symbol", "type": "string"}
        ],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    # ...省略其余的 ABI 元素
]

# 连接合约
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# 铸造 NFT
nonce = w3.eth.get_transaction_count(account.address)
tokenId = 1  # 这里填写您想要铸造的 NFT 的 ID
txn = contract.functions.claim(account.address, tokenId).buildTransaction({
    'from': account.address,
    'nonce': nonce,
    'gas': 200000,
    'gasPrice': w3.toWei('50', 'gwei')
})

# 签名并发送交易
signed_txn = w3.eth.account.sign_transaction(txn, private_key)
txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)

print(f"Transaction sent with hash: {txn_hash.hex()}")

def signChallenge(challenge):
    sk = private_key  # 使用实际的私钥替换
    acct = w3.eth.account.from_key(sk)
    signed_message = acct.sign_message(challenge)
    return acct.address, signed_message.signature

def verifySig():
    challenge_bytes = random.randbytes(32)
    challenge = encode_defunct(challenge_bytes)
    address, sig = signChallenge(challenge)
    return w3.eth.account.recover_message(challenge, signature=sig) == address

if __name__ == '__main__':
    if verifySig():
        print("You passed the challenge!")
    else:
        print("You failed the challenge!")

