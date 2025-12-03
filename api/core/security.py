from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import JWTError, jwt

from .core import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)

# ==================================
# 1. Password Hashing
# ==================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")

    # bcrypt 72 bytes limit
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        password = password_bytes.decode("utf-8", errors="ignore")

    return pwd_context.hash(password)


# ==================================
# 2. JWT Tokens
# ==================================

def create_access_token(data: dict) -> str:
    """
    Create a short-lived Access Token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """
    Create a long-lived Refresh Token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ==================================
# 3. Verify Token (🔥 완전 수정된 정답 버전)
# ==================================

def verify_token(token: str):
    """
    Verify JWT and return the full decoded payload:
    {
        "sub": username,
        "user_id": "...",
        "exp": ...
    }
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # 필수 필드 확인
        if "sub" not in payload or "user_id" not in payload:
            return None

        return payload   # ⭐ dict 전체 반환해야 FastAPI Depends 정상 작동

    except JWTError:
        return None
