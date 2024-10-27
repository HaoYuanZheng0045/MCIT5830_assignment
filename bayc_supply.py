from web3 import Web3
from web3.providers.rpc import HTTPProvider
import requests
import json

# Infura 项目 ID，用于连接以太坊节点
INFURA_PROJECT_ID = "f6a0ee81e7ec415ca7891993229af4b5"  # 替换为您的实际项目 ID
INFURA_URL = f"https://mainnet.infura.io/v3/f6a0ee81e7ec415ca7891993229af4b5"

# Bored Ape 合约地址
bayc_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
contract_address = Web3.to_checksum_address(bayc_address)


# 获取合约 ABI
ABI_ENDPOINT = 'https://api.etherscan.io/api?module=contract&action=getabi&address='
response = requests.get(f"{ABI_ENDPOINT}{contract_address}", timeout=20)
abi = json.loads(response.json()['result'])

# 连接到以太坊节点
provider = HTTPProvider(INFURA_URL)
web3 = Web3(provider)

# 实例化合约并获取总供应量
contract = web3.eth.contract(address=contract_address, abi=abi)
supply = contract.functions.totalSupply().call()

print(f"Supply = {supply}")
