# api/core/security.py

from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import EmailStr

# core 설정값 불러오기
# ⚠ 상대 import가 아니라 절대 import 사용해야 함 (FastAPI 프로덕션 권장)
from api.core import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS
)

# ================================
# 1. 비밀번호 해시 (Password Hashing)
# ================================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """입력된 비밀번호(plain)과 DB에 저장된 해시를 비교"""
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    """비밀번호를 bcrypt로 해시"""
    return pwd_context.hash(password)


# ================================
# 2. JWT 토큰 생성
# ================================
def create_access_token(data: dict) -> str:
    """
    Access Token 생성 (유효기간: ACCESS_TOKEN_EXPIRE_MINUTES)
    payload 구조:
        {
            "sub": 이메일,
            "exp": 만료시간
        }
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Refresh Token 생성 (유효기간: REFRESH_TOKEN_EXPIRE_DAYS)"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ================================
# 3. JWT 토큰 검증
# ================================
def verify_token(token: str) -> EmailStr | None:
    """
    JWT 토큰을 검증하고 payload['sub'](이메일)을 반환.
    실패 시 None 반환.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")

        if sub is None:
            return None

        return sub

    except JWTError as e:
        # 만료 / 위조 / 시그니처 오류 등
        print(f"[JWTError] 토큰 검증 실패: {e}")
        return None
