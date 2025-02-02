from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from app.core.config import settings
import base64
import os

# 初始化加密密鑰，如果沒有則跳出警告
if not settings.WALLET_ENCRYPTION_KEY:
    raise ValueError(
        "WALLET_ENCRYPTION_KEY is not set. Please provide a valid key in the environment variables."
    )
password = settings.WALLET_ENCRYPTION_KEY.encode()


# 生成 RSA 公私鑰對
def generate_key_pair():
    """
    生成 RSA 公私鑰對，返回加密的私鑰、公鑰及隨機 salt。
    """
    # 由於安全性考慮，這裡的代碼不提供示範，請自行實現
    return private_key_pem, public_key_pem, base64.b64encode(salt).decode("utf-8")


# 加密和解密函數
def encrypt_wallet_address(wallet_address: str):
    """
    使用公鑰加密錢包地址，並返回加密後的地址/私鑰/Salt。
    """
    # 由於安全性考慮，這裡的代碼不提供示範，請自行實現

    return (
        base64.urlsafe_b64encode(encrypted_address).decode(),
        base64.b64encode(private_key_pem).decode("utf-8"),
        salt_b64,  # 返回加密所用的 salt
    )


def decrypt_wallet_address(
    encrypted_address: str, private_key_pem: str, salt_b64: str
) -> str:
    """
    使用私鑰和隨機 salt 解密錢包地址。
    """
    # 由於安全性考慮，這裡的代碼不提供示範，請自行實現
    return decrypted_address.decode()


# 示例使用
if __name__ == "__main__":
    original_address = "0x1234567890ABCDEF1234567890ABCDEF12345678"
    encrypted, private_key, salt = encrypt_wallet_address(original_address)
    decrypted = decrypt_wallet_address(encrypted, private_key, salt)

    print(f"Original Address: {original_address}")
    print(f"Encrypted Address: {encrypted}")
    print(f"Decrypted Address: {decrypted}")
    print(f"Private Key: {private_key}")
