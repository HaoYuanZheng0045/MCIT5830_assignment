from web3 import Web3
from eth_account.messages import encode_defunct
import random
from eth_account import Account

def signChallenge(challenge):
    # 使用您的私钥创建账户
    sk = "0xa589a20c9e95a2218f4ebb69e564527e1e2f5cb673958d32f93cd0399dee04cf"  # 替换为您的私钥
    acct = Account.from_key(sk)

    # 将 challenge 转换为字节类型
    if isinstance(challenge, bytes):
        pass  # 已是字节类型，直接使用
    elif isinstance(challenge, str):
        challenge = challenge.encode('utf-8')  # 转换为字节
    else:
        raise ValueError("Challenge must be a string or bytes.")

    # 使用 encode_defunct 进行编码并签名
    message = encode_defunct(hexstr=challenge.hex())
    signed_message = acct.sign_message(message)

    # 返回地址和签名
    return acct.address, signed_message.signature

def verifySig():
    """
    自动评分器将用于测试 signChallenge 的代码
    """
    # 生成32字节的随机挑战
    challenge_bytes = random.randbytes(32)
    challenge = encode_defunct(hexstr=challenge_bytes.hex())

    # 使用 signChallenge 函数签名消息
    address, sig = signChallenge(challenge_bytes)

    # 验证签名是否正确
    w3 = Web3()
    return w3.eth.account.recover_message(challenge, signature=sig) == address

if __name__ == '__main__':
    # 测试您的函数
    if verifySig():
        print("You passed the challenge!")
    else:
        print("You failed the challenge!")



