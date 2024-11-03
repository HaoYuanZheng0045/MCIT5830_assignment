from web3 import Web3
from eth_account.messages import encode_defunct
import os
from eth_account import Account

def signChallenge(challenge):
    # 使用您的私钥创建账户
    sk = "0xa589a20c9e95a2218f4ebb69e564527e1e2f5cb673958d32f93cd0399dee04cf"  # 替换为您的私钥
    acct = Account.from_key(sk)

    # 确保 challenge 是字节类型
    if not isinstance(challenge, bytes):
        challenge = bytes(challenge)

    # 使用 encode_defunct 对 challenge 编码并签名
    message = encode_defunct(challenge)
    signed_message = acct.sign_message(message)

    # 返回地址和签名
    return acct.address, signed_message.signature

def verifySig():
    """
    自动评分器将用于测试 signChallenge 的代码
    """
    # 生成32字节的随机挑战
    challenge_bytes = os.urandom(32)

    # 使用 signChallenge 函数签名消息
    address, sig = signChallenge(challenge_bytes)

    # 验证签名是否正确
    w3 = Web3()
    message = encode_defunct(challenge_bytes)
    return w3.eth.account.recover_message(message, signature=sig) == address

if __name__ == '__main__':
    # 测试您的函数
    if verifySig():
        print("You passed the challenge!")
    else:
        print("You failed the challenge!")




