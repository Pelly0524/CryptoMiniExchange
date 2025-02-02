from sqlalchemy import Column, Integer, String, Text, ForeignKey
from app.models.base import Base


# 核心錢包子錢包資料表的模型
class CoreWalletSubWallet(Base):
    __tablename__ = "core_wallet_sub_wallet"

    SubWalletID = Column(Integer, primary_key=True, autoincrement=True)
    AccountID = Column(String, ForeignKey("account.AccountID"), nullable=False)
    SubWalletAddress = Column(String, nullable=False, unique=True)
    EncryptedPrivateKey = Column(Text, nullable=False)  # 加密後的私鑰
    KeyMaterial = Column(Text, nullable=False)  # 通用名稱表示私鑰的存儲
    Salt = Column(Text, nullable=False)
