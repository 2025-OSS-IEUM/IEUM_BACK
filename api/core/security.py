# api/core/security.py

from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import EmailStr

# 1.core.py에서 .env로부터 읽어온 설정값들을 가져옵니다.
from .core import (
    SECRET_KEY, 
    ALGORITHM, 
    ACCESS_TOKEN_EXPIRE_MINUTES, 
    REFRESH_TOKEN_EXPIRE_DAYS
)
# ==================================
# 1. 비밀번호 해시 (Password Hashing)
# ==================================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    입력된 비밀번호(plain)와 저장된 해시(hashed)를 비교합니다.
    """
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """
    bcrypt는 최대 72 bytes만 처리 가능하므로,
    그보다 길면 잘라서 해시 오류를 방지한다.
    """
    password_bytes = password.encode("utf-8")

    # 72 bytes 초과 방지
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        password = password_bytes.decode("utf-8", errors="ignore")

    return pwd_context.hash(password)
# ==================================
# 2. JWT 토큰 (JWT Token)
# ==================================

def create_access_token(data: dict) -> str:
    """
    Access Token을 생성합니다.
    """
    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) -> str:
    """
    Refresh Token을 생성합니다. (API 명세: 14일)
    """
    to_encode = data.copy()
    
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> EmailStr | str | None:
    """
    토큰을 검증하고, 유효하다면 Payload의 'sub' 값을 반환합니다.
    (이 함수는 나중에 '/users/me' 같은 인증이 필요한 API에서 사용됩니다)
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        sub: EmailStr | str | None = payload.get("sub")
        
        if sub is None:
            return None # 'sub'가 없으면 유효하지 않은 토큰
            
        return sub
    
    except JWTError:
        # 토큰이 만료되었거나 형식이 잘못된 경우
        return None