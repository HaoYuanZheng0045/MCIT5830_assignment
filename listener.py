from web3 import Web3
from web3.contract import Contract
from web3.providers.rpc import HTTPProvider
from web3.middleware import geth_poa_middleware  # Necessary for POA chains
import json
from datetime import datetime
import pandas as pd

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
    if chain == 'avax':
        api_url = f"https://api.avax-test.network/ext/bc/C/rpc"  # AVAX C-chain testnet

    if chain == 'bsc':
        api_url = f"https://data-seed-prebsc-1-s1.binance.org:8545/"  # BSC testnet

    if chain in ['avax', 'bsc']:
        w3 = Web3(Web3.HTTPProvider(api_url))
        # inject the POA compatibility middleware to the innermost layer
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    else:
        w3 = Web3(Web3.HTTPProvider(api_url))

    # Deposit Event ABI
    DEPOSIT_ABI = json.loads('[ { "anonymous": false, "inputs": [ { "indexed": true, "internalType": "address", "name": "token", "type": "address" }, { "indexed": true, "internalType": "address", "name": "recipient", "type": "address" }, { "indexed": false, "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "Deposit", "type": "event" }]')
    contract = w3.eth.contract(address=contract_address, abi=DEPOSIT_ABI)

    arg_filter = {}

    # Handle 'latest' block
    if start_block == "latest":
        start_block = w3.eth.get_block_number()
    if end_block == "latest":
        end_block = w3.eth.get_block_number()

    if end_block < start_block:
        print(f"Error: end_block < start_block!")
        print(f"end_block = {end_block}")
        print(f"start_block = {start_block}")
        return

    if start_block == end_block:
        print(f"Scanning block {start_block} on {chain}")
    else:
        print(f"Scanning blocks {start_block} - {end_block} on {chain}")

    # Prepare CSV header if file doesn't exist
    columns = ['chain', 'token', 'recipient', 'amount', 'transactionHash', 'address', 'date']
    try:
        pd.read_csv(eventfile)
    except FileNotFoundError:
        df = pd.DataFrame(columns=columns)
        df.to_csv(eventfile, index=False, mode='w', header=True)

    # Handle blocks in the specified range
    rows = []
    if end_block - start_block < 30:
        event_filter = contract.events.Deposit.create_filter(fromBlock=start_block, toBlock=end_block, argument_filters=arg_filter)
        events = event_filter.get_all_entries()
        
        # Process events and store them in rows
        for evt in events:
            data = {
                'chain': chain,
                'token': evt.args['token'],
                'recipient': evt.args['recipient'],
                'amount': evt.args['amount'],
                'transactionHash': evt.transactionHash.hex(),
                'address': evt.address,
                'date': datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            }
            rows.append(data)
    
    else:
        for block_num in range(start_block, end_block + 1):
            event_filter = contract.events.Deposit.create_filter(fromBlock=block_num, toBlock=block_num, argument_filters=arg_filter)
            events = event_filter.get_all_entries()
            
            # Process events for each block
            for evt in events:
                data = {
                    'chain': chain,
                    'token': evt.args['token'],
                    'recipient': evt.args['recipient'],
                    'amount': evt.args['amount'],
                    'transactionHash': evt.transactionHash.hex(),
                    'address': evt.address,
                    'date': datetime.now().strftime("%m/%d/%Y %H:%M:%S")
                }
                rows.append(data)

    # Write the rows to the CSV file
    if rows:
        df = pd.DataFrame(rows, columns=columns)
        df.to_csv(eventfile, index=False, mode='a', header=False)
        print(f"Successfully scanned {len(rows)} events and saved to {eventfile}.")
    else:
        print("No events found in the specified block range.")


