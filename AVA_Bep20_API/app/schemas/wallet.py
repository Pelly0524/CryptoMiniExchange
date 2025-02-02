from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from dataclasses import dataclass


class WalletCreate(BaseModel):
    id: int
    account: str
    address: str
    balance: Decimal = 0.0

    class Config:
        from_attributes = True


class WalletBalanceFromBlockChain(BaseModel):
    id: int
    address: str
    balance: list[dict]


class WalletBalanceFromSystem(BaseModel):
    CurrencyID: int
    AvailableBalance: Decimal
    LockedBalance: Decimal
    LastUpdatedTime: datetime
