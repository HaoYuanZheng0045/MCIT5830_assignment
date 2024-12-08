from web3 import Web3
from web3.contract import Contract
from web3.providers.rpc import HTTPProvider
from web3.middleware import geth_poa_middleware  # Necessary for POA chains
import json
import sys
from pathlib import Path
import time

source_chain = 'avax'
destination_chain = 'bsc'
contract_info = "contract_info.json"

def connectTo(chain):
    """
    Connect to the Avalanche or BNB chain testnet
    """
    if chain == 'avax':
        api_url = f"https://api.avax-test.network/ext/bc/C/rpc"  # AVAX C-chain testnet

    if chain == 'bsc':
        api_url = f"https://data-seed-prebsc-1-s1.binance.org:8545/"  # BSC testnet

    if chain in ['avax', 'bsc']:
        w3 = Web3(Web3.HTTPProvider(api_url))
        # Inject the POA compatibility middleware to the innermost layer
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        if not w3.isConnected():
            print(f"Failed to connect to {chain} chain")
            sys.exit(1)
        return w3

def getContractInfo(chain):
    """
    Load the contract_info file into a dictionary
    This function is used by the autograder and will likely be useful to you
    """
    p = Path(__file__).with_name(contract_info)
    try:
        with p.open('r') as f:
            contracts = json.load(f)
    except Exception as e:
        print("Failed to read contract info")
        print(f"Please contact your instructor. Error: {e}")
        sys.exit(1)

    return contracts[chain]

def registerSourceToken():
    """
    Register source token on the source contract
    """
    w3 = connectTo("avax")
    contract_info = getContractInfo("avax")
    source_contract = w3.eth.contract(address=contract_info["source_contract_address"], abi=contract_info["source_contract_abi"])

    # Register source chain token
    tokens = read_erc20s()
    for token in tokens:
        source_token_address = token['source_chain_token_address']
        txn = source_contract.functions.registerToken(source_token_address).buildTransaction({
            'from': w3.eth.defaultAccount,
            'gas': 2000000,
            'gasPrice': w3.toWei('5', 'gwei'),
            'nonce': w3.eth.getTransactionCount(w3.eth.defaultAccount),
        })
        
        signed_txn = w3.eth.account.signTransaction(txn, private_key="your_private_key")
        tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(f"Registered token {source_token_address} on source chain, tx hash: {tx_hash.hex()}")
        w3.eth.waitForTransactionReceipt(tx_hash)
        print("Token registration confirmed on source chain")

def registerDestinationToken():
    """
    Register destination token on the destination contract
    """
    w3 = connectTo("bsc")
    contract_info = getContractInfo("bsc")
    destination_contract = w3.eth.contract(address=contract_info["destination_contract_address"], abi=contract_info["destination_contract_abi"])

    # Register destination chain token
    tokens = read_erc20s()
    for token in tokens:
        destination_token_address = token['destination_chain_token_address']
        txn = destination_contract.functions.createToken(destination_token_address).buildTransaction({
            'from': w3.eth.defaultAccount,
            'gas': 2000000,
            'gasPrice': w3.toWei('5', 'gwei'),
            'nonce': w3.eth.getTransactionCount(w3.eth.defaultAccount),
        })
        
        signed_txn = w3.eth.account.signTransaction(txn, private_key="your_private_key")
        tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
        print(f"Created token {destination_token_address} on destination chain, tx hash: {tx_hash.hex()}")
        w3.eth.waitForTransactionReceipt(tx_hash)
        print("Token creation confirmed on destination chain")

def scanBlocks(chain):
    """
    Scan the last few blocks for 'Deposit' or 'Unwrap' events
    When 'Deposit' is found on the source chain, call wrap() on the destination chain
    When 'Unwrap' is found on the destination chain, call withdraw() on the source chain
    """
    if chain not in ['source', 'destination']:
        print(f"Invalid chain: {chain}")
        return

    if chain == "source":
        w3 = connectTo("avax")
        contract_info = getContractInfo("avax")
        source_contract = w3.eth.contract(address=contract_info["source_contract_address"], abi=contract_info["source_contract_abi"])
        event_filter = source_contract.events.Deposit.createFilter(fromBlock="latest", toBlock="latest")
        events = event_filter.get_all_entries()

        for event in events:
            # Call wrap() on the destination contract when Deposit event is found
            print(f"Deposit event found on source chain, calling wrap on destination chain")
            wrapOnDestination(event)

    elif chain == "destination":
        w3 = connectTo("bsc")
        contract_info = getContractInfo("bsc")
        destination_contract = w3.eth.contract(address=contract_info["destination_contract_address"], abi=contract_info["destination_contract_abi"])
        event_filter = destination_contract.events.Unwrap.createFilter(fromBlock="latest", toBlock="latest")
        events = event_filter.get_all_entries()

        for event in events:
            # Call withdraw() on the source contract when Unwrap event is found
            print(f"Unwrap event found on destination chain, calling withdraw on source chain")
            withdrawOnSource(event)

def wrapOnDestination(event):
    """
    When a Deposit event occurs on the source chain, call wrap on the destination chain
    """
    w3 = connectTo("bsc")
    contract_info = getContractInfo("bsc")
    destination_contract = w3.eth.contract(address=contract_info["destination_contract_address"], abi=contract_info["destination_contract_abi"])

    txn = destination_contract.functions.wrap(event.args.amount).buildTransaction({
        'from': w3.eth.defaultAccount,
        'gas': 2000000,
        'gasPrice': w3.toWei('5', 'gwei'),
        'nonce': w3.eth.getTransactionCount(w3.eth.defaultAccount),
    })

    signed_txn = w3.eth.account.signTransaction(txn, private_key="your_private_key")
    tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    print(f"Wrapped {event.args.amount} tokens on destination chain, tx hash: {tx_hash.hex()}")
    w3.eth.waitForTransactionReceipt(tx_hash)
    print("Wrap action confirmed on destination chain")

def withdrawOnSource(event):
    """
    When an Unwrap event occurs on the destination chain, call withdraw on the source chain
    """
    w3 = connectTo("avax")
    contract_info = getContractInfo("avax")
    source_contract = w3.eth.contract(address=contract_info["source_contract_address"], abi=contract_info["source_contract_abi"])

    txn = source_contract.functions.withdraw(event.args.amount).buildTransaction({
        'from': w3.eth.defaultAccount,
        'gas': 2000000,
        'gasPrice': w3.toWei('5', 'gwei'),
        'nonce': w3.eth.getTransactionCount(w3.eth.defaultAccount),
    })

    signed_txn = w3.eth.account.signTransaction(txn, private_key="your_private_key")
    tx_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    print(f"Withdrew {event.args.amount} tokens on source chain, tx hash: {tx_hash.hex()}")
    w3.eth.waitForTransactionReceipt(tx_hash)
    print("Withdraw action confirmed on source chain")

# Main function: Register tokens and listen for events
if __name__ == "__main__":
    print("Registering tokens...")
    registerSourceToken()  # Register tokens on source chain
    registerDestinationToken()  # Register tokens on destination chain

    while True:
        print("Scanning source chain for Deposit events...")
        scanBlocks("source")  # Listen for Deposit events on the source chain
        
        print("Scanning destination chain for Unwrap events...")
        scanBlocks("destination")  # Listen for Unwrap events on the destination chain

        # Wait a bit before scanning again to avoid hitting rate limits
        time.sleep(10)

        
        # Wait a bit before scanning again to avoid hitting rate limits
        time.sleep(10)





