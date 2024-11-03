from web3 import Web3
from eth_account.messages import encode_defunct
import random
from eth_account import Account

def signChallenge(challenge):
    # 使用提供的私钥
    sk = "0xa589a20c9e95a2218f4ebb69e564527e1e2f5cb673958d32f93cd0399dee04cf"
    acct = Account.from_key(sk)
    
    # 将挑战消息编码成适合签名的格式
    if isinstance(challenge, bytes):  # 如果challenge是字节格式
        challenge_message = encode_defunct(challenge)
    else:
        challenge_message = encode_defunct(text=challenge)
    
    # 使用账户签名消息
    signed_message = acct.sign_message(challenge_message)
    
    # 返回签名
    return signed_message.signature

def verifySig():
    """
    自动评分器将用于测试 signChallenge 的代码
    """
    # 生成32字节的随机挑战
    challenge_bytes = random.randbytes(32)
    
    # 调用 signChallenge 来获取签名
    sig = signChallenge(challenge_bytes)
    
    # 使用私钥生成账户地址，并验证签名
    account = Account.from_key("0xa589a20c9e95a2218f4ebb69e564527e1e2f5cb673958d32f93cd0399dee04cf")
    challenge_message = encode_defunct(challenge_bytes)
    return Web3().eth.account.recover_message(challenge_message, signature=sig) == account.address

if __name__ == '__main__':
    # 测试你的函数
    if verifySig():
        print("You passed the challenge!")
    else:
        print("You failed the challenge!")



