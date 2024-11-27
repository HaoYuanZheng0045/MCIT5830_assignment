from web3 import Web3
from web3.middleware import geth_poa_middleware  # Necessary for POA chains
import json
from datetime import datetime
import pandas as pd

# Define the event log file
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
    # Set RPC URL based on the chain type
    if chain == 'avax':
        api_url = "https://api.avax-test.network/ext/bc/C/rpc"  # AVAX C-chain testnet
    elif chain == 'bsc':
        api_url = "https://data-seed-prebsc-1-s1.binance.org:8545/"  # BSC testnet
    else:
        raise ValueError("Unsupported chain. Use 'avax' or 'bsc'.")

    # Connect to the blockchain
    w3 = Web3(Web3.HTTPProvider(api_url))

    # Inject POA middleware if necessary (for Avalanche and BSC)
    if chain in ['avax', 'bsc']:
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    # Deposit event ABI (simplified to include only the Deposit event)
    DEPOSIT_ABI = json.loads('[ { "anonymous": false, "inputs": [ { "indexed": true, "internalType": "address", "name": "token", "type": "address" }, { "indexed": true, "internalType": "address", "name": "recipient", "type": "address" }, { "indexed": false, "internalType": "uint256", "name": "amount", "type": "uint256" } ], "name": "Deposit", "type": "event" }]')

    # Create the contract instance
    contract = w3.eth.contract(address=contract_address, abi=DEPOSIT_ABI)

    # Handle 'latest' blocks
    if start_block == "latest":
        start_block = w3.eth.get_block_number()
    if end_block == "latest":
        end_block = w3.eth.get_block_number()

    # Ensure valid block range
    if end_block < start_block:
        print(f"Error: end_block < start_block!")
        return

    print(f"Scanning blocks from {start_block} to {end_block} on {chain}")

    # List to store event logs
    logs = []

    # If block range is small, get events in bulk
    if end_block - start_block < 30:
        event_filter = contract.events.Deposit.createFilter(fromBlock=start_block, toBlock=end_block)
        events = event_filter.get_all_entries()

        # Process the events
        for evt in events:
            token = evt.args['token']
            recipient = evt.args['recipient']
            amount = evt.args['amount']
            transaction_hash = evt.transactionHash.hex()
            contract_address = evt.address

            # Get block timestamp and format it
            timestamp = datetime.utcfromtimestamp(w3.eth.getBlock(evt.blockNumber)['timestamp'])
            formatted_time = timestamp.strftime('%m/%d/%Y %H:%M:%S')

            logs.append([chain, token, recipient, amount, transaction_hash, contract_address, formatted_time])

    else:
        # If block range is large, scan block by block
        for block_num in range(start_block, end_block + 1):
            event_filter = contract.events.Deposit.createFilter(fromBlock=block_num, toBlock=block_num)
            events = event_filter.get_all_entries()

            for evt in events:
                token = evt.args['token']
                recipient = evt.args['recipient']
                amount = evt.args['amount']
                transaction_hash = evt.transactionHash.hex()
                contract_address = evt.address

                # Get block timestamp and format it
                timestamp = datetime.utcfromtimestamp(w3.eth.getBlock(evt.blockNumber)['timestamp'])
                formatted_time = timestamp.strftime('%m/%d/%Y %H:%M:%S')

                logs.append([chain, token, recipient, amount, transaction_hash, contract_address, formatted_time])

    # Write the data to a CSV file using pandas
    df = pd.DataFrame(logs, columns=['chain', 'token', 'recipient', 'amount', 'transactionHash', 'address', 'date'])

    # Append data to CSV file (create the file if it doesn't exist)
    df.to_csv(eventfile, mode='a', header=not bool(pd.io.common.get_file_contents(eventfile)), index=False)

    print(f"Logs written to {eventfile}")
