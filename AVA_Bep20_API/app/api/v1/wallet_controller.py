from fastapi import APIRouter, HTTPException, Depends, status
from decimal import Decimal
from app.schemas.wallet import (
    WalletCreate,
    WalletBalanceFromBlockChain,
    WalletBalanceFromSystem,
)
from app.services.wallet_service import WalletService
from app.repositories.wallet_repository import WalletRepository
from app.core.security import get_current_user
from app.utils.encryption import encrypt_wallet_address
from app.core.dependencies import get_wallet_repository, get_wallet_service

wallet_router = APIRouter()


@wallet_router.post(
    "/create", response_model=WalletCreate, status_code=status.HTTP_201_CREATED
)
async def create_wallet(
    user: str = Depends(get_current_user),
    wallet_repository: WalletRepository = Depends(get_wallet_repository),
    wallet_service: WalletService = Depends(get_wallet_service),
):
    """
    創建新 BEP20 錢包
    """
    # 檢查用戶是否已經擁有錢包
    existing_wallet = wallet_repository.get_wallet_by_user(user)
    if existing_wallet:
        raise HTTPException(
            status_code=status.HTTP_200_OK, detail="User already has a wallet"
        )

    try:
        # 創建新錢包並保存到資料庫
        new_wallet_data = wallet_service.create_wallet()
        encrypt_data = encrypt_wallet_address(new_wallet_data[1])  # 加密錢包的私鑰
        new_wallet = wallet_repository.save_wallet(
            user, new_wallet_data[0], encrypt_data[0], encrypt_data[1], encrypt_data[2]
        )

        return WalletCreate(
            id=new_wallet.SubWalletID,
            account=new_wallet.AccountID,
            address=new_wallet.SubWalletAddress,
            balance=Decimal(0.0),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create wallet: {str(e)}",
        )


@wallet_router.get(
    "/balance-from-blockchain", response_model=WalletBalanceFromBlockChain
)
def get_wallet_balance(
    user: str = Depends(get_current_user),
    wallet_repository: WalletRepository = Depends(get_wallet_repository),
    wallet_service: WalletService = Depends(get_wallet_service),
):
    """
    查詢指定 BEP20 錢包的餘額
    """
    try:
        wallet = wallet_repository.get_wallet_by_user(user)
        balance = wallet_service.get_asset_balances_from_blockchain(
            wallet.SubWalletAddress
        )
        return WalletBalanceFromBlockChain(
            id=wallet.SubWalletID, address=wallet.SubWalletAddress, balance=balance
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@wallet_router.get("/balance-from-system", response_model=list[WalletBalanceFromSystem])
def get_wallet_balance_from_db(
    user: str = Depends(get_current_user),
    wallet_repository: WalletRepository = Depends(get_wallet_repository),
):
    """
    從資料庫查詢錢包餘額
    """
    try:
        # 獲取用戶的錢包
        wallet = wallet_repository.get_wallet_by_user(user)
        if not wallet:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found"
            )

        # 查詢資料庫餘額
        balances = wallet_repository.get_system_balance_by_wallet(wallet.SubWalletID)
        return balances
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@wallet_router.get("/check", status_code=status.HTTP_200_OK)
async def check_wallet_exists(
    user: str = Depends(get_current_user),
    wallet_repository: WalletRepository = Depends(get_wallet_repository),
):
    """
    檢查目前的使用者是否已經擁有錢包
    """
    # 查詢使用者的錢包
    wallet = wallet_repository.get_wallet_by_user(user)
    if wallet:
        return {
            "has_wallet": True,
            "message": "User already has a wallet.",
            "address": wallet.SubWalletAddress,
        }
    else:
        return {"has_wallet": False, "message": "User does not have a wallet yet."}
