import jwt as pyjwt  # 確保調用的是 PyJWT
import pytz
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from app.schemas.token import TokenData
from sqlalchemy.orm import Session
from app.models.account import Account
from app.db.session import SessionLocal
from app.core.config import settings


# 用於生成 JWT Token 的函數
def create_jwt_token(account: str, security_key: str) -> str:
    """
    創建 JWT token，包含用戶名為 claims。
    :param account: 用戶名或帳號
    :param security_key: 用於簽名的密鑰
    :return: JWT token 字符串
    """

    # 由於安全性考慮，這裡的代碼不提供示範，請自行實現

    return token


# 用於解碼和驗證 JWT Token 的函數
def decode_and_verify_token(token):
    try:

        # 由於安全性考慮，這裡的代碼不提供示範，請自行實現

        return {"success": True, "data": decoded_token}
    except pyjwt.ExpiredSignatureError:
        return {"success": False, "message": "Token 已過期"}
    except pyjwt.InvalidTokenError as e:
        return {"success": False, "message": f"無效的 Token: {str(e)}"}


# 用於解碼和驗證 JWT Token 的函數
async def get_current_user(
    token: str = Depends(OAuth2PasswordBearer(tokenUrl="token")),
):
    # 由於安全性考慮，這裡的代碼不提供示範，請自行實現

    return user_id


# 將時間戳轉換為指定時區的本地時間
def timestamp_to_local_time(timestamp, timezone="Asia/Taipei"):

    base_time = datetime.datetime(1970, 1, 1) + timedelta(seconds=timestamp)
    target_timezone = pytz.timezone(timezone)  # 指定目標時區
    local_time = base_time.replace(tzinfo=pytz.utc).astimezone(target_timezone)
    return local_time.strftime("%Y-%m-%d %H:%M:%S")
