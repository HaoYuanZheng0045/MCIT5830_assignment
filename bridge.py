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

# Connect to a blockchain (either Avalanche or BNB Testnet)
def connectTo(chain):
    if chain == 'avax':
        api_url = f"https://api.avax-test.network/ext/bc/C/rpc"  # AVAX C-chain testnet
    elif chain == 'bsc':
        api_url = f"https://data-seed-prebsc-1-s1.binance.org:8545/"  # BSC testnet

    if chain in ['avax', 'bsc']:
        w3 = Web3(Web3.HTTPProvider(api_url))
        # Inject POA compatibility middleware to the innermost layer
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        if not w3.isConnected():
            print(f"Failed to connect to {chain} chain")
            sys.exit(1)
        return w3

# Load the contract information from the contract_info.json file
def getContractInfo(chain):
    p = Path(__file__).with_name(contract_info)
    try:
        with p.open('r') as f:
            contracts = json.load(f)
    except Exception as e:
        print("Failed to read contract info")
        print(f"Error: {e}")
        sys.exit(1)

    return contracts[chain]

# Listen for events from the source or destination chain and call the corresponding function
def scanBlocks(chain):
    if chain == "source":
        w3 = connectTo("avax")
        contract_info = getContractInfo("avax")
        source_contract = w3.eth.contract(address=contract_info["source_contract_address"], abi=contract_info["source_contract_abi"])
        event_filter = source_contract.events.Deposit.createFilter(fromBlock="latest", toBlock="latest")
        events = event_filter.get_all_entries()

        for event in events:
            # When a "Deposit" event is found on the source chain, call wrap on the destination chain
            print(f"Deposit event found on source chain, calling wrap on destination chain")
            wrapOnDestination(event)

    elif chain == "destination":
        w3 = connectTo("bsc")
        contract_info = getContractInfo("bsc")
        destination_contract = w3.eth.contract(address=contract_info["destination_contract_address"], abi=contract_info["destination_contract_abi"])
        event_filter = destination_contract.events.Unwrap.createFilter(fromBlock="latest", toBlock="latest")
        events = event_filter.get_all_entries()

        for event in events:
            # When an "Unwrap" event is found on the destination chain, call withdraw on the source chain
            print(f"Unwrap event found on destination chain, calling withdraw on source chain")
            withdrawOnSource(event)

    else:
        print(f"Invalid chain: {chain}")
        return

# Call the wrap() function on the destination contract
def wrapOnDestination(event):
    w3 = connectTo("bsc")
    contract_info = getContractInfo("bsc")
    destination_contract = w3.eth.contract(address=contract_info["destination_contract_address"], abi=contract_info["destination_contract_abi"])
    
    # Use the 'warden' private key to sign the transaction
    txn = destination_contract.functions.wrap(event.args.amount).buildTransaction({
        'from': w3.eth.defaultAccount,
        'gas': 2000000,
        'gasPrice': w3.toWei('5', 'gwei'),
        'nonce': w3.eth.getTransactionCount(w3.eth.defaultAccount),
    })
    
    signed_txn = w3.eth.account.signTransaction(txn, private_key="your_private_key")
    w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    print(f"Wrapped {event.args.amount} tokens on destination chain")

# Call the withdraw() function on the source contract
def withdrawOnSource(event):
    w3 = connectTo("avax")
    contract_info = getContractInfo("avax")
    source_contract = w3.eth.contract(address=contract_info["source_contract_address"], abi=contract_info["source_contract_abi"])
    
    # Use the 'warden' private key to sign the transaction
    txn = source_contract.functions.withdraw(event.args.amount).buildTransaction({
        'from': w3.eth.defaultAccount,
        'gas': 2000000,
        'gasPrice': w3.toWei('5', 'gwei'),
        'nonce': w3.eth.getTransactionCount(w3.eth.defaultAccount),
    })
    
    signed_txn = w3.eth.account.signTransaction(txn, private_key="your_private_key")
    w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    print(f"Withdrew {event.args.amount} tokens on source chain")

# Main function that runs the bridge process and keeps listening
if __name__ == "__main__":
    while True:
        print("Scanning source chain for Deposit events...")
        scanBlocks("source")  # Listen for events on the source chain
        
        print("Scanning destination chain for Unwrap events...")
        scanBlocks("destination")  # Listen for events on the destination chain
        
        # Wait a bit before scanning again to avoid hitting rate limits
        time.sleep(10)



