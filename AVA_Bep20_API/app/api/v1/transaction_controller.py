from fastapi import APIRouter, HTTPException, Depends, status, Body
from decimal import Decimal
from app.schemas.transaction import TransactionResult
from app.services.transaction_service import TransactionService
from app.repositories.wallet_repository import WalletRepository
from app.repositories.transaction_repository import TransactionRepository
from app.core.security import get_current_user
from app.core.dependencies import (
    get_wallet_repository,
    get_transaction_service,
    get_transaction_repository,
)

transaction_router = APIRouter()


@transaction_router.get("/get-deposit-transactions")
def get_deposit_transactions(
    user: str = Depends(get_current_user),
    wallet_repository: WalletRepository = Depends(get_wallet_repository),
    transaction_repository: TransactionRepository = Depends(get_transaction_repository),
):
    """
    取得用戶的入金交易記錄
    """
    user_wallet = wallet_repository.get_wallet_by_user(user)
    return transaction_repository.get_deposit_transactions_by_wallet(
        user_wallet.SubWalletID
    )


@transaction_router.get("/get-withdraw-transactions")
def get_withdraw_transactions(
    user: str = Depends(get_current_user),
    wallet_repository: WalletRepository = Depends(get_wallet_repository),
    transaction_repository: TransactionRepository = Depends(get_transaction_repository),
):
    """
    取得用戶的提領交易記錄
    """
    user_wallet = wallet_repository.get_wallet_by_user(user)
    return transaction_repository.get_withdraw_transactions_by_wallet(
        user_wallet.SubWalletID
    )


@transaction_router.post("/withdraw-usdt", response_model=TransactionResult)
def withdraw_usdt(
    recipient_address: str = Body(..., embed=True),
    amount: Decimal = Body(..., embed=True),
    user: str = Depends(get_current_user),
    transaction_service: TransactionService = Depends(get_transaction_service),
    wallet_repository: WalletRepository = Depends(get_wallet_repository),
    transaction_repository: TransactionRepository = Depends(get_transaction_repository),
):
    """
    進行 USDT 代幣提領(扣除系統餘額)
    """

    try:
        # 手續費 1 USDT
        fee = Decimal(1)
        # 取得user錢包
        user_wallet = wallet_repository.get_wallet_by_user(user)
        # 檢查用戶USDT餘額是否足夠
        user_system_balance = wallet_repository.get_system_balance_by_wallet(
            user_wallet.SubWalletID
        )
        result = [
            balance["AvailableBalance"]
            for balance in user_system_balance
            if balance["CurrencyID"] == 2
        ]
        available_balance = result[0] if result else 0

        if available_balance < amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User USDT balance is not enough",
            )

        if amount < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Amount must be greater than $10 USDT",
            )

        # 進行提領交易(核心錢包地址發送)
        real_withdraw_amount = amount - fee
        transaction_result = transaction_service.withdraw_system_usdt(
            recipient_address, real_withdraw_amount
        )

        if not transaction_result.success:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY, detail="Transfer failed"
            )

        # 呼叫存儲程序進行提領交易(扣除系統餘額)
        transaction_repository.execute_withdraw_transaction(
            from_sub_wallet_id=user_wallet.SubWalletID,
            currency_id=2,
            to_address=transaction_result.recipient_address,
            amount=amount,
            gas_used=transaction_result.gas_used,
            fee=fee,
            tx_hash=transaction_result.tx_hash,
        )

        return transaction_result
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


# @transaction_router.post(
#     "/withdraw-bnb", response_model=TransactionResult, status_code=status.HTTP_200_OK
# )
# def transfer_bnb(
#     recipient_address: str = Body(..., embed=True),
#     amount: Decimal = Body(..., embed=True),
#     user: str = Depends(get_current_user),
#     transaction_service: TransactionService = Depends(get_transaction_service),
#     wallet_repository: WalletRepository = Depends(get_wallet_repository),
#     transaction_repository: TransactionRepository = Depends(get_transaction_repository),
# ):
#     """
#     進行 BNB 代幣轉帳
#     """

#     try:
#         # 取得user錢包並解密私鑰
#         user_wallet = wallet_repository.get_wallet_by_user(user)

#         sender_private_key = decrypt_wallet_address(
#             user_wallet.EncryptedPrivateKey, user_wallet.KeyMaterial, user_wallet.Salt
#         )

#         # 進行轉帳
#         transaction_result = transaction_service.transfer_bnb(
#             sender_private_key, recipient_address, amount
#         )

#         # 保存交易到資料庫
#         transaction_repository.execute_withdraw_transaction(
#             from_sub_wallet_id=user_wallet.SubWalletID,
#             currency_id=1,
#             to_address=transaction_result.recipient_address,
#             amount=transaction_result.amount,
#             gas_used=transaction_result.gas_used,
#             fee=0.1,
#             tx_hash=transaction_result.tx_hash,
#         )

#         return transaction_result
#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
