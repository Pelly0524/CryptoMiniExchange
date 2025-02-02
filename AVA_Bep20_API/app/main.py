from fastapi import FastAPI
from app.core.config import setup_cors
from app.routes import setup_routes
from app.core.lifespan import lifespan
from app.core.logger import logger
import os

# 創建 FastAPI 應用程序實例
app = FastAPI(title="BEP20 Wallet API", version="1.0.0", lifespan=lifespan)

# 配置 CORS
setup_cors(app)

# 設置路由
setup_routes(app)


# 根路徑測試
@app.get("/")
async def root():
    return {"message": "Welcome to the BEP20 Wallet API"}


# 啟動 HTTPS 的入口
if __name__ == "__main__":
    try:
        # 根據當前工作目錄動態構造檔案路徑
        base_dir = os.path.abspath(os.path.dirname(__file__))  # 獲取 /app 目錄路徑
        ssl_certfile = os.path.join(base_dir, "../xxxx.crt")
        ssl_keyfile = os.path.join(base_dir, "../xxxx.key")

        # 啟動 Uvicorn 服務
        import uvicorn

        uvicorn.run(
            "app.main:app",  # 注意要用完整模組路徑
            host="0.0.0.0",
            port=8080,
            ssl_certfile=ssl_certfile,  # 自簽憑證檔案路徑
            ssl_keyfile=ssl_keyfile,  # 私鑰檔案路徑
            access_log=False,  # 關閉訪問日誌
        )
    except Exception as e:
        logger.info(f"Error starting server: {e}")
