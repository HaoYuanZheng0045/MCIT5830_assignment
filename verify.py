from web3 import Web3
from eth_account.messages import encode_defunct
import random

# 实例化 Web3
w3 = Web3()

def signChallenge(challenge):
    # 使用实际的私钥替换
    sk = "0xa589a20c9e95a2218f4ebb69e564527e1e2f5cb673958d32f93cd0399dee04cf"  # 确保用正确的私钥填充此处

    acct = w3.eth.account.from_key(sk)

    # 签署挑战消息
    signed_message = acct.sign_message(challenge)

    return acct.address, signed_message.signature

def verifySig():
    """
    测试 signChallenge 函数的代码
    """
    challenge_bytes = random.randbytes(32)
    challenge = encode_defunct(challenge_bytes)
    address, sig = signChallenge(challenge)

    # 验证签名是否正确
    return w3.eth.account.recover_message(challenge, signature=sig) == address

if __name__ == '__main__':
    if verifySig():
        print("You passed the challenge!")
    else:
        print("You failed the challenge!")
