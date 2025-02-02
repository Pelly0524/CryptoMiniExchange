from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.base import Base
from app.core.config import settings
from dotenv import load_dotenv

# 確保載入環境變數
load_dotenv()

# 驗證 DATABASE_URL 是否正確設定
if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL 未設置，請檢查設定或 .env 文件")

# 創建資料庫引擎
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # 在調試階段顯示 SQL 語句，生產環境可設為 False
    pool_size=10,  # 設置連接池大小
    max_overflow=20,  # 超出連接池大小的額外連接數量
    pool_timeout=30,  # 連接超時秒數
    pool_recycle=1800,  # 回收空閒連接，防止 MySQL 的空閒連接超時
)

# 建立資料庫會話工廠
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 資料庫會話依賴，用於 FastAPI
def get_db():
    """
    生成資料庫會話並確保在使用後正確關閉
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 初始化資料庫表，只需執行一次
def init_db():
    """
    初始化資料庫表結構
    """
    try:
        Base.metadata.create_all(bind=engine)
        print("資料庫表初始化成功")
    except Exception as e:
        print(f"資料庫表初始化失敗: {e}")


if __name__ == "__main__":
    init_db()
