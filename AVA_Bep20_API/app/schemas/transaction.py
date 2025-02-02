from dataclasses import dataclass
from typing import Optional
from decimal import Decimal


@dataclass
class TransactionResult:
    success: bool
    timestamp: str
    tx_hash: Optional[str] = None
    sender_address: Optional[str] = None
    recipient_address: Optional[str] = None
    amount: Optional[Decimal] = None
    gas_used: Optional[Decimal] = None
    error_message: Optional[str] = None

    class Config:
        smart_union = True  # 自動嘗試轉換兼容類型
