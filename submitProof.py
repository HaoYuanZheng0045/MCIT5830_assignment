import eth_account
import random
import string
import json
from pathlib import Path
from web3 import Web3
from web3.middleware import geth_poa_middleware
import math

def merkle_assignment():
    num_of_primes = 8192
    primes = generate_primes(num_of_primes)

    if len(primes) != num_of_primes:
        print(f"Error: Expected {num_of_primes} primes, but got {len(primes)}.")
        return

    if primes[-1] != 84017:
        print(f"Error: The 8192nd prime is {primes[-1]}, expected 84017.")
        return

    leaves = convert_leaves(primes)

    chain = 'bsc'
    w3 = connect_to(chain)
    if w3 is None:
        print("Error: Failed to connect to the blockchain.")
        return
    address, abi = get_contract_info(chain)
    contract = w3.eth.contract(address=address, abi=abi)

    random_leaf_index = select_unclaimed_leaf(w3, contract, leaves, num_of_primes)
    if random_leaf_index is None:
        print("Error: No unclaimed leaves available.")
        return

    merkle_tree = build_merkle(leaves)
    proof = prove_merkle(merkle_tree, random_leaf_index)

    challenge = ''.join(random.choice(string.ascii_letters) for _ in range(32))
    addr, sig = sign_challenge(challenge)

    print(f"Address: {addr}")
    print(f"Signature: {sig}")

    if sign_challenge_verify(challenge, addr, sig):
        tx_hash = send_signed_msg(w3, contract, proof, leaves[random_leaf_index])
        print(f"Transaction hash: {tx_hash}")
    else:
        print("Error: Signature verification failed.")

def generate_primes(num_primes):
    sieve_size = 2000000
    sieve = [True] * sieve_size
    sieve[0:2] = [False, False]
    primes = []
    for p in range(2, sieve_size):
        if sieve[p]:
            primes.append(p)
            if len(primes) >= num_primes:
                break
            for multiple in range(p * p, sieve_size, p):
                sieve[multiple] = False
    if len(primes) < num_primes:
        raise ValueError("Sieve size too small to generate the required number of primes.")
    return primes

def convert_leaves(primes_list):
    return [prime.to_bytes(32, 'big') for prime in primes_list]

def build_merkle(leaves):
    tree = [leaves]
    current_level = leaves
    while len(current_level) > 1:
        next_level = []
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            right = current_level[i + 1] if i + 1 < len(current_level) else left
            parent_hash = hash_pair(left, right)
            next_level.append(parent_hash)
        tree.append(next_level)
        current_level = next_level
    return tree

def prove_merkle(merkle_tree, random_indx):
    merkle_proof = []
    index = random_indx
    for level in merkle_tree[:-1]:
        sibling_index = index ^ 1
        if sibling_index < len(level):
            sibling = level[sibling_index]
        else:
            sibling = level[index]
        merkle_proof.append(sibling)
        index = index // 2
    return merkle_proof

def select_unclaimed_leaf(w3, contract, leaves, num_of_primes):
    for attempt in range(10000):
        index = random.randint(1, num_of_primes - 1)
        prime = int.from_bytes(leaves[index], 'big')
        try:
            owner = contract.functions.getOwnerByPrime(prime).call()
            if owner == '0x0000000000000000000000000000000000000000':
                return index
        except Exception as e:
            print(f"Error checking owner for prime {prime}: {e}")
    return None

def sign_challenge(challenge):
    acct = get_account()
    eth_encoded_msg = eth_account.messages.encode_defunct(text=challenge)
    eth_sig_obj = eth_account.Account.sign_message(eth_encoded_msg, private_key=acct.key)
    return acct.address, eth_sig_obj.signature.hex()

def send_signed_msg(w3, contract, proof, random_leaf):
    acct = get_account()

    print("Available functions in the contract:")
    for func in contract.abi:
        if func['type'] == 'function':
            print(func['name'])

    try:
        submit_func = contract.functions.submit
    except AttributeError:
        print("Error: 'submit' function not found in the contract ABI.")
        return '0x'

    try:
        tx = submit_func(proof, random_leaf).build_transaction({
            'from': acct.address,
            'nonce': w3.eth.get_transaction_count(acct.address),
            'gas': 500000,
            'maxFeePerGas': w3.to_wei('20', 'gwei'),
            'maxPriorityFeePerGas': w3.to_wei('1', 'gwei'),
            'chainId': 97
        })
        print(f"Transaction dict: {tx}")
    except Exception as e:
        print(f"Error building transaction: {e}")
        return '0x'

    try:
        signed_tx = w3.eth.account.sign_transaction(tx, acct.key)
        print(f"Signed transaction: {signed_tx}")
    except Exception as e:
        print(f"Error signing transaction: {e}")
        return '0x'

    try:
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"Transaction hash: {tx_hash.hex()}")
    except Exception as e:
        print(f"Error sending transaction: {e}")
        return '0x'

    try:
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)
        if receipt.status == 1:
            print("Transaction successful!")
        else:
            print("Transaction failed!")
    except Exception as e:
        print(f"Error waiting for transaction receipt: {e}")

    return tx_hash.hex()


def connect_to(chain):
    if chain not in ['avax', 'bsc']:
        print(f"{chain} is not a valid option for 'connect_to()'")
        return None
    if chain == 'avax':
        api_url = "https://api.avax-test.network/ext/bc/C/rpc"
    else:
        api_url = "https://data-seed-prebsc-1-s1.binance.org:8545/"
    w3 = Web3(Web3.HTTPProvider(api_url))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3

def get_account():
    cur_dir = Path(__file__).parent.absolute()
    with open(cur_dir.joinpath('sk.txt'), 'r') as f:
        sk = f.readline().strip()
    if sk.startswith("0x"):
        sk = sk[2:]
    return eth_account.Account.from_key(sk)

def get_contract_info(chain):
    cur_dir = Path(__file__).parent.absolute()
    with open(cur_dir.joinpath("contract_info.json"), "r") as f:
        d = json.load(f)
    return d[chain]['address'], d[chain]['abi']

def sign_challenge_verify(challenge, addr, sig):
    eth_encoded_msg = eth_account.messages.encode_defunct(text=challenge)
    recovered_addr = eth_account.Account.recover_message(eth_encoded_msg, signature=sig)
    if recovered_addr == addr:
        print(f"Success: signed the challenge {challenge} using address {addr}!")
        return True
    else:
        print(f"Failure: The signature does not verify!")
        print(f"signature = {sig}\naddress = {addr}\nchallenge = {challenge}")
        return False

def hash_pair(a, b):
    return Web3.solidity_keccak(['bytes32', 'bytes32'], [min(a, b), max(a, b)])

if __name__ == "__main__":
    merkle_assignment()













