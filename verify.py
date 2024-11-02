from web3 import Web3
from eth_account.messages import encode_defunct
import random
import json

def generate_new_account():
    w3 = Web3()
    new_account = w3.eth.account.create()
    print("生成的地址:", new_account.address)
    print("生成的私钥:", new_account.privateKey.hex())
    return new_account

def signChallenge(challenge):
    # Web3连接到Avalanche Fuji测试网
    w3 = Web3(Web3.HTTPProvider('https://api.avax-test.network/ext/bc/C/rpc'))

    # 生成新的账户和私钥
    acct = generate_new_account()

    # 对挑战字符串进行签名
    signed_message = w3.eth.account.sign_message(challenge, private_key=acct._private_key)

    return acct.address, signed_message.signature

def verifySig():
    """
    这是autograder将用来测试signChallenge的代码
    """

    # 随机生成32字节的挑战字符串
    challenge_bytes = random.randbytes(32)
    challenge = encode_defunct(challenge_bytes)

    # 获取地址和签名
    address, sig = signChallenge(challenge)

    # 验证签名是否正确
    w3 = Web3(Web3.HTTPProvider('https://api.avax-test.network/ext/bc/C/rpc'))
    return w3.eth.account.recover_message(challenge, signature=sig) == address

if __name__ == '__main__':
    """
    测试函数
    """
    if verifySig():
        print("You passed the challenge!")
    else:
        print("You failed the challenge!")


