from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
from app.db.session import SessionLocal
from decimal import Decimal
from app.models.core_wallet_transaction import (
    CoreWalletTransaction,
    TransactionTypeEnum,
)


class TransactionRepository:
    def __init__(self):
        """
        初始化 Repository
        """

    def get_transaction_by_id(self, transaction_id: int) -> CoreWalletTransaction:
        """
        根據交易 ID 查詢交易記錄
        """
        with SessionLocal() as session:
            return (
                session.query(CoreWalletTransaction)
                .filter(CoreWalletTransaction.TransactionID == transaction_id)
                .first()
            )

    def get_deposit_transactions_by_wallet(
        self, sub_wallet_id: int
    ) -> list[CoreWalletTransaction]:
        """
        根據 SubWalletID 查詢入金交易記錄
        """
        with SessionLocal() as session:
            return (
                session.query(CoreWalletTransaction)
                .filter(
                    (CoreWalletTransaction.SubWalletID == sub_wallet_id)
                    & (
                        CoreWalletTransaction.TransactionType
                        == TransactionTypeEnum.deposit
                    )
                )
                .all()
            )

    def get_withdraw_transactions_by_wallet(
        self, sub_wallet_id: int
    ) -> list[CoreWalletTransaction]:
        """
        根據 SubWalletID 查詢提領交易記錄
        """
        with SessionLocal() as session:
            return (
                session.query(CoreWalletTransaction)
                .filter(
                    (CoreWalletTransaction.SubWalletID == sub_wallet_id)
                    & (
                        CoreWalletTransaction.TransactionType
                        == TransactionTypeEnum.withdrawal
                    )
                )
                .all()
            )

    def get_recent_transactions(self, limit: int = 10) -> list[CoreWalletTransaction]:
        """
        查詢最近的交易記錄
        """
        with SessionLocal() as session:
            return (
                session.query(CoreWalletTransaction)
                .order_by(CoreWalletTransaction.CreateTime.desc())
                .limit(limit)
                .all()
            )

    def execute_withdraw_transaction(
        self,
        from_sub_wallet_id: int,
        currency_id: int,
        to_address: str,
        amount: Decimal,
        gas_used: Decimal,
        fee: Decimal,
        tx_hash: str,
    ):
        """
        呼叫存儲過程執行提領交易
        """
        with SessionLocal() as session:
            try:
                # 建立存儲程序的執行 SQL
                sql = text(
                    """
                    CALL core_wallet_WithdrawTransaction(
                        :from_sub_wallet_id,
                        :currency_id,
                        :to_address,
                        :amount,
                        :gas,
                        :fee,
                        :tx_hash
                    )
                    """
                )
                # 執行存儲程序
                session.execute(
                    sql,
                    {
                        "from_sub_wallet_id": from_sub_wallet_id,
                        "currency_id": currency_id,
                        "to_address": to_address,
                        "amount": amount,
                        "gas": gas_used,
                        "fee": fee,
                        "tx_hash": tx_hash,
                    },
                )
                # 提交事務
                session.commit()
            except SQLAlchemyError as e:
                # 發生錯誤時回滾
                session.rollback()
                print(f"Error occurred while executing withdraw transaction: {e}")
                raise e
