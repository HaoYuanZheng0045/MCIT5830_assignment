import eth_account
import random
import string
import json
from pathlib import Path
from web3 import Web3
from web3.middleware import geth_poa_middleware  # Necessary for POA chains


def merkle_assignment():
    num_of_primes = 8192
    primes = generate_primes(num_of_primes)
    leaves = convert_leaves(primes)
    tree = build_merkle(leaves)
    random_leaf_index = random.randint(1, len(primes) - 1)
    proof = prove_merkle(tree, random_leaf_index)
    challenge = ''.join(random.choice(string.ascii_letters) for i in range(32))
    addr, sig = sign_challenge(challenge)

    if sign_challenge_verify(challenge, addr, sig):
        tx_hash = send_signed_msg(proof, leaves[random_leaf_index])
        print(f"Transaction hash: {tx_hash}")


def generate_primes(num_primes):
    primes_list = []
    candidate = 2
    while len(primes_list) < num_primes:
        is_prime = all(candidate % p != 0 for p in primes_list)
        if is_prime:
            primes_list.append(candidate)
        candidate += 1
    return primes_list


def convert_leaves(primes_list):
    leaves = [int.to_bytes(prime, 32, 'big') for prime in primes_list]
    return leaves


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
    proof = []
    index = random_indx
    for level in merkle_tree[:-1]:  # Skip root level
        pair_index = index ^ 1  # Get sibling index
        if pair_index < len(level):
            proof.append(level[pair_index])
        index //= 2  # Move to the next level
    return proof


def sign_challenge(challenge):
    acct = get_account()
    eth_encoded_msg = eth_account.messages.encode_defunct(text=challenge)
    signature = acct.sign_message(eth_encoded_msg)
    return acct.address, signature.signature.hex()


def send_signed_msg(proof, random_leaf):
    chain = 'bsc'
    acct = get_account()
    address, abi = get_contract_info(chain)
    w3 = connect_to(chain)
    contract = w3.eth.contract(address=address, abi=abi)

    # Convert random_leaf to bytes if necessary
    if isinstance(random_leaf, int):
        random_leaf = random_leaf.to_bytes(32, 'big')

    # Build the transaction
    tx = contract.functions.submit(proof, random_leaf).buildTransaction({
        'from': acct.address,
        'nonce': w3.eth.get_transaction_count(acct.address),
        'gas': 300000,
        'gasPrice': Web3.to_wei(20, 'gwei')
    })

    # Sign the transaction locally
    signed_tx = w3.eth.account.sign_transaction(tx, acct.key)

    # Send the signed transaction
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    return tx_hash.hex()




# Helper functions that do not need to be modified
def connect_to(chain):
    if chain not in ['avax', 'bsc']:
        print(f"{chain} is not a valid option for 'connect_to()'")
        return None
    if chain == 'avax':
        api_url = f"https://api.avax-test.network/ext/bc/C/rpc"  # AVAX C-chain testnet
    else:
        api_url = f"https://data-seed-prebsc-1-s1.binance.org:8545/"  # BSC testnet
    w3 = Web3(Web3.HTTPProvider(api_url))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3


def get_account():
    cur_dir = Path(__file__).parent.absolute()
    with open(cur_dir.joinpath('sk.txt'), 'r') as f:
        sk = f.readline().rstrip()
    if sk[0:2] == "0x":
        sk = sk[2:]
    return eth_account.Account.from_key(sk)


def get_contract_info(chain):
    cur_dir = Path(__file__).parent.absolute()
    with open(cur_dir.joinpath("contract_info.json"), "r") as f:
        d = json.load(f)
        d = d[chain]
    return d['address'], d['abi']


def sign_challenge_verify(challenge, addr, sig):
    eth_encoded_msg = eth_account.messages.encode_defunct(text=challenge)
    if eth_account.Account.recover_message(eth_encoded_msg, signature=sig) == addr:
        print(f"Success: signed the challenge {challenge} using address {addr}!")
        return True
    else:
        print(f"Failure: The signature does not verify!")
        print(f"signature = {sig}\naddress = {addr}\nchallenge = {challenge}")
        return False


def hash_pair(a, b):
    if a < b:
        return Web3.solidity_keccak(['bytes32', 'bytes32'], [a, b])
    else:
        return Web3.solidity_keccak(['bytes32', 'bytes32'], [b, a])


if __name__ == "__main__":
    merkle_assignment()













