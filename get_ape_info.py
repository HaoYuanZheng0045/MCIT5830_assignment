from web3 import Web3
from web3.providers.rpc import HTTPProvider
import requests
import json

# Infura 项目 ID，用于连接以太坊节点
INFURA_PROJECT_ID = "f6a0ee81e7ec415ca7891993229af4b5"  # 替换为您的实际项目 ID
INFURA_URL = f"https://mainnet.infura.io/v3/f6a0ee81e7ec415ca7891993229af4b5"

# Bored Ape 合约地址和 ABI
bayc_address = "0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D"
contract_address = Web3.to_checksum_address(bayc_address)


# 从本地加载合约 ABI
with open('/home/codio/workspace/abi.json', 'r') as f:
    abi = json.load(f)

# 连接到以太坊节点
provider = HTTPProvider(INFURA_URL)
web3 = Web3(provider)
contract = web3.eth.contract(address=contract_address, abi=abi)

def get_ape_info(apeID):
    assert isinstance(apeID, int), f"{apeID} is not an int"
    assert 1 <= apeID, f"{apeID} must be at least 1"

    data = {'owner': "", 'image': "", 'eyes': ""}

    try:
        owner = contract.functions.ownerOf(apeID).call()
        data['owner'] = owner

        token_uri = contract.functions.tokenURI(apeID).call()

        if token_uri.startswith("ipfs://"):
            token_uri = token_uri.replace("ipfs://", "https://ipfs.io/ipfs/")

        response = requests.get(token_uri)
        if response.status_code == 200:
            metadata = response.json()
            data['image'] = metadata.get('image', "")

            attributes = metadata.get('attributes', [])
            for attribute in attributes:
                if attribute.get('trait_type') == 'Eyes':
                    data['eyes'] = attribute.get('value', "")
                    break
        else:
            print(f"Failed to fetch metadata for Ape ID {apeID}. Status code: {response.status_code}")

    except Exception as e:
        print(f"An error occurred while fetching info for Ape ID {apeID}: {e}")

    assert isinstance(data, dict), f'get_ape_info{apeID} should return a dict' 
    assert all([a in data.keys() for a in ['owner', 'image', 'eyes']]), "Return value should include keys 'owner', 'image', and 'eyes'"
    return data


