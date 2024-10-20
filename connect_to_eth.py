import json
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.providers.rpc import HTTPProvider

'''If you use one of the suggested infrastructure providers, the url will be of the form
now_url  = f"https://eth.nownodes.io/{now_token}"
alchemy_url = f"https://eth-mainnet.alchemyapi.io/v2/{alchemy_token}"
infura_url = f"https://mainnet.infura.io/v3/{infura_token}"
'''


def connect_to_eth():
    url = "https://mainnet.infura.io/v3/4eea275f633744c2a75821eb1fbc6194"  # 替换为你的Infura项目ID
    w3 = Web3(HTTPProvider(url))
    assert w3.is_connected(), f"Failed to connect to provider at {url}"  # 使用 is_connected() 方法
    return w3


def connect_with_middleware(contract_json):
    with open(contract_json, "r") as f:
        d = json.load(f)
        d = d['bsc']
        address = d['address']
        abi = d['abi']

    url = "https://bsc-testnet.nodereal.io/v1/d67eb1208ab14a6ebde6dac342a999b0"
    w3 = Web3(HTTPProvider(url))
    
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    assert w3.is_connected(), f"Failed to connect to provider at {url}" 
    
    contract = w3.eth.contract(address=address, abi=abi)
    
    return w3, contract


if __name__ == "__main__":
    # Connect to Ethereum mainnet
    w3 = connect_to_eth()
    print("Connected to Ethereum mainnet:", w3.is_connected())
    
    # Connect to BNB testnet and create contract object
    w3_bnb, contract = connect_with_middleware('contract_info.json')
    print("Connected to BNB testnet:", w3_bnb.is_connected())
    print("Contract address:", contract.address)
