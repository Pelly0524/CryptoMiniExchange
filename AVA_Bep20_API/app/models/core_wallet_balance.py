from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from app.models.base import Base


class CoreWalletBalance(Base):
    __tablename__ = "core_wallet_balance"

    BalanceID = Column(Integer, primary_key=True, autoincrement=True)
    SubWalletID = Column(
        Integer, ForeignKey("core_wallet_sub_wallet.SubWalletID"), nullable=False
    )
    CurrencyID = Column(
        Integer, ForeignKey("core_wallet_currency.CurrencyID"), nullable=False
    )
    AvailableBalance = Column(Numeric(20, 10), nullable=False, default=0)
    LockedBalance = Column(Numeric(20, 10), nullable=False, default=0)
    LastUpdatedTime = Column(DateTime, nullable=False)
