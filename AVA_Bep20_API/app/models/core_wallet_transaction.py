from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    Enum,
    Boolean,
    ForeignKey,
)
from app.models.base import Base
from enum import Enum as PyEnum


# 定義交易類型的 Enum
class TransactionTypeEnum(PyEnum):
    deposit = "deposit"
    withdrawal = "withdrawal"
    transfer = "transfer"
    refund = "refund"


# 核心錢包交易紀錄資料表的模型
class CoreWalletTransaction(Base):
    __tablename__ = "core_wallet_transaction"

    TransactionID = Column(Integer, primary_key=True, autoincrement=True)
    SubWalletID = Column(
        Integer, ForeignKey("core_wallet_sub_wallet.SubWalletID"), nullable=False
    )
    CurrencyID = Column(
        Integer, ForeignKey("core_wallet_currency.CurrencyID"), nullable=False
    )
    RecipientAddress = Column(String(255), nullable=True)
    Amount = Column(Numeric(20, 10), nullable=False)
    GasUsed = Column(Numeric(20, 10), nullable=True)
    TxHash = Column(String(255), nullable=True)
    TransactionType = Column(Enum(TransactionTypeEnum), nullable=False)
    Success = Column(Boolean, default=True, nullable=False)
    CreateTime = Column(DateTime, nullable=False)
