from web3 import Web3
from eth_account.messages import encode_defunct
import random
from eth_account import Account

def signChallenge(challenge):
    # 这里填入你的私钥
    sk = "0xa589a20c9e95a2218f4ebb69e564527e1e2f5cb673958d32f93cd0399dee04cf"
    acct = Account.from_key(sk)
    
    # 将挑战消息编码成适合签名的格式
    message = encode_defunct(text=challenge)
    signed_message = acct.sign_message(message)
    
    # 返回签名对象
    return signed_message.signature

def verifySig():
    """
    这是自动评分器将用于测试 signChallenge 的代码
    """
    # 生成随机挑战字节串
    challenge_bytes = random.randbytes(32)
    
    # 将挑战编码成适合签名的格式
    challenge = encode_defunct(challenge_bytes)
    sig = signChallenge(challenge_bytes)
    
    # 重新生成地址并验证签名
    address = Account.from_key("YOUR_SECRET_KEY_HERE").address
    return w3.eth.account.recover_message(challenge, signature=sig) == address

if __name__ == '__main__':
    # 测试你的函数
    if verifySig():
        print("You passed the challenge!")
    else:
        print("You failed the challenge!")


