import asyncio
from app.core.logger import logger
from contextlib import asynccontextmanager
from app.services.monitor_service import MonitorService
from app.repositories.monitored_repository import MonitoredRepository
from app.repositories.wallet_repository import WalletRepository
from app.services.transaction_service import TransactionService


@asynccontextmanager
async def lifespan(app):
    """
    Lifespan context manager，用於處理應用的啟動和關閉事件
    """
    logger.info("Application startup: Initializing resources.")

    # 手動初始化依賴
    monitored_repository = MonitoredRepository()
    wallet_repository = WalletRepository()
    transaction_service = TransactionService()
    monitor_service = MonitorService(
        monitored_repository, wallet_repository, transaction_service
    )

    # 啟動監聽任務
    refresh_task = asyncio.create_task(monitor_service.refresh_addresses())
    monitor_task = asyncio.create_task(monitor_service.monitor_blockchain())

    # 提供 lifespan scope 的上下文
    yield

    logger.info("Application shutdown: Cleaning up resources.")
    refresh_task.cancel()
    monitor_task.cancel()

    # 確保取消的任務已完成
    await asyncio.gather(refresh_task, monitor_task, return_exceptions=True)
