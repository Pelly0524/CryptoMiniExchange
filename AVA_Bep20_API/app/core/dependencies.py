from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.session import get_db
from app.services.wallet_service import WalletService
from app.services.transaction_service import TransactionService
from app.repositories.wallet_repository import WalletRepository
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.monitored_repository import MonitoredRepository


# wallet_service
def get_wallet_service() -> WalletService:
    return WalletService()


# wallet_repository
def get_wallet_repository() -> WalletRepository:
    return WalletRepository()


# transaction_service
def get_transaction_service() -> TransactionService:
    return TransactionService()


# transaction_repository
def get_transaction_repository() -> TransactionRepository:
    return TransactionRepository()


# monitored_repository
def get_monitored_repository() -> MonitoredRepository:
    return MonitoredRepository()
