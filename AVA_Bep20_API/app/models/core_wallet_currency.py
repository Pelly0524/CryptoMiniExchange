from sqlalchemy import Column, Integer, String
from app.models.base import Base


class CoreWalletCurrency(Base):
    __tablename__ = "core_wallet_currency"

    CurrencyID = Column(Integer, primary_key=True, autoincrement=True)
    CurrencyCode = Column(String(10), nullable=False, unique=True)
