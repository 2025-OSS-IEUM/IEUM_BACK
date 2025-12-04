from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import EmailStr

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


def verify_token(token: str) -> str | None: # 👈 반환 타입을 EmailStr에서 str로 변경
    """
    토큰을 검증하고, 유효하다면 Payload의 'sub' 값을 반환합니다.
    (이 함수는 나중에 '/users/me' 같은 인증이 필요한 API에서 사용됩니다)
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # sub의 타입 힌트에서 EmailStr 제거
        sub: str | None = payload.get("sub") 
        
        if sub is None:
            return None # 'sub'가 없으면 유효하지 않은 토큰
            
        return sub # ⭐ 이제 유저 이름(username)이 반환됩니다.
    
    except JWTError:
        # 토큰이 만료되었거나 형식이 잘못된 경우
        return None