# Settings
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # 資料庫連接 URL
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    # JWT 相關設定
    JWT_SECRET_KEY: str = Field(..., env="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS512"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # BSC 節點 URL
    BSC_MAINNET_NODE_URL: str = Field(..., env="BSC_MAINNET_NODE_URL")
    BSC_TESTNET_NODE_URL: str = Field(..., env="BSC_TESTNET_NODE_URL")
    # 錢包加密金鑰
    WALLET_ENCRYPTION_KEY: str = Field(..., env="WALLET_ENCRYPTION_KEY")
    # USDT 合約地址
    USDT_CONTRACT_ADDRESS: str = Field(..., env="USDT_CONTRACT_ADDRESS")
    # Method ID
    TRANSFER_METHOD_ID: str = Field(..., env="TRANSFER_METHOD_ID")
    # 核心錢包資訊
    CORE_WALLET_ADDRESS: str = Field(..., env="CORE_WALLET_ADDRESS")
    CORE_WALLET_PRIVATE_KEY: str = Field(..., env="CORE_WALLET_PRIVATE_KEY")

    # 指定 .env 檔案
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()

# 設置 CORS
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app: FastAPI):
    """
    配置 CORS 中介層
    """
    origins = ["http://localhost", "http://localhost:3000", "*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
