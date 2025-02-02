import logging


# 初始化 Uvicorn 的 logger
def get_logger(name: str = "uvicorn"):
    """
    獲取指定名稱的 logger，默認為 Uvicorn 的 logger。
    """
    logger = logging.getLogger(name)
    return logger


# 預設導出 Uvicorn 的 logger
logger = get_logger()
