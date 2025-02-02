from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from app.db.session import SessionLocal
from decimal import Decimal
from app.models.core_wallet_sub_wallet import CoreWalletSubWallet


class MonitoredRepository:
    def __init__(self):
        """
        初始化 Repository
        """

    def get_all_addresses(self):
        """
        獲取所有需要監聽的地址
        """
        with SessionLocal() as session:
            wallets = session.query(CoreWalletSubWallet).all()
            return [wallet.SubWalletAddress for wallet in wallets]

    def execute_deposit_transaction(
        self,
        sub_wallet_id: int,
        currency_id: int,
        amount: Decimal,
        fee: Decimal,
        tx_hash: str,
    ):
        """
        呼叫存儲程序 core_wallet_DepositTransaction 進行存款交易
        """
        with SessionLocal() as session:
            try:
                # 建立存儲程序的執行 SQL
                sql = text(
                    """
                    CALL core_wallet_DepositTransaction(:sub_wallet_id, :currency_id, :amount, :fee, :tx_hash)
                    """
                )
                # 執行存儲程序
                session.execute(
                    sql,
                    {
                        "sub_wallet_id": sub_wallet_id,
                        "currency_id": currency_id,
                        "amount": amount,
                        "fee": fee,
                        "tx_hash": tx_hash,
                    },
                )
                # 提交變更
                session.commit()
            except Exception as e:
                # 回滾交易以避免資料損壞
                session.rollback()
                raise e
