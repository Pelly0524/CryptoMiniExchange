from fastapi import FastAPI
from app.api.v1.wallet_controller import wallet_router
from app.api.v1.transaction_controller import transaction_router


def setup_routes(app: FastAPI):
    """
    設置應用的所有路由
    """
    app.include_router(wallet_router, prefix="/api/v1/wallet", tags=["wallet"])
    app.include_router(
        transaction_router, prefix="/api/v1/transaction", tags=["transaction"]
    )
