from web3 import Web3
import eth_account
import os

def get_keys(challenge, keyId=0, filename="eth_mnemonic.txt"):
    """
    Generate a stable private key
    challenge - byte string
    keyId (integer) - which key to use
    filename - filename to read and store mnemonics

    Each mnemonic is stored on a separate line
    If fewer than (keyId+1) mnemonics have been generated, generate a new one and return that
    """

    w3 = Web3()

    msg = eth_account.messages.encode_defunct(challenge)

    # 读取或生成助记词
    if os.path.exists(filename):
        with open(filename, "r") as f:
            mnemonics = f.readlines()
    else:
        mnemonics = []

    # 生成新的私钥（如果没有足够的助记词）
    if keyId >= len(mnemonics):
        acct = eth_account.Account.create()
        private_key = acct._private_key.hex()  # 使用 _private_key 而不是 privateKey
        mnemonics.append(private_key + "\n")
        with open(filename, "w") as f:
            f.writelines(mnemonics)
    else:
        private_key = mnemonics[keyId].strip()

    acct = eth_account.Account.from_key(private_key)
    eth_addr = acct.address

    # 对消息进行签名
    sig = acct.sign_message(msg)

    # 验证签名
    assert eth_account.Account.recover_message(msg, signature=sig.signature.hex()) == eth_addr, "Failed to sign message properly"

    # 返回签名和地址
    return sig, eth_addr

if __name__ == "__main__":
    for i in range(4):
        challenge = os.urandom(64)
        sig, addr = get_keys(challenge=challenge, keyId=i)
        print(addr)
