from sqlalchemy.orm import Session
from app.models.core_wallet_sub_wallet import CoreWalletSubWallet
from app.models.core_wallet_balance import CoreWalletBalance
from app.db.session import SessionLocal


class WalletRepository:
    def __init__(self):
        """
        初始化 Repository
        """

    def save_wallet(
        self,
        account_id: str,
        wallet_address: str,
        encrypted_private_key: str,
        key_material: str,
        salt: str,
    ) -> CoreWalletSubWallet:
        """
        保存新生成的子錢包至資料庫
        """
        with SessionLocal() as session:
            try:
                new_wallet = CoreWalletSubWallet(
                    AccountID=account_id,
                    SubWalletAddress=wallet_address,
                    EncryptedPrivateKey=encrypted_private_key,
                    KeyMaterial=key_material,
                    Salt=salt,
                )
                session.add(new_wallet)
                session.commit()
                session.refresh(new_wallet)
                return new_wallet
            except Exception as e:
                session.rollback()
                raise e

    def get_wallet_by_address(self, wallet_address: str) -> CoreWalletSubWallet:
        """
        根據錢包地址查詢子錢包資料
        """
        with SessionLocal() as session:
            return (
                session.query(CoreWalletSubWallet)
                .filter(CoreWalletSubWallet.SubWalletAddress == wallet_address)
                .first()
            )

    def get_wallet_by_user(self, user_name: str) -> CoreWalletSubWallet:
        """
        根據使用者查詢子錢包資料
        """
        with SessionLocal() as session:
            return (
                session.query(CoreWalletSubWallet)
                .filter(CoreWalletSubWallet.AccountID == user_name)
                .first()
            )

    def get_system_balance_by_wallet(self, sub_wallet_id: int) -> list[dict]:
        """
        根據子錢包 ID 查詢所有餘額資訊。
        """
        with SessionLocal() as session:
            try:
                balances = (
                    session.query(CoreWalletBalance)
                    .filter(CoreWalletBalance.SubWalletID == sub_wallet_id)
                    .all()
                )

                # 格式化資料為 list[dict]
                return [
                    {
                        "CurrencyID": balance.CurrencyID,
                        "AvailableBalance": float(balance.AvailableBalance),
                        "LockedBalance": float(balance.LockedBalance),
                        "LastUpdatedTime": balance.LastUpdatedTime,
                    }
                    for balance in balances
                ]
            except Exception as e:
                raise e
