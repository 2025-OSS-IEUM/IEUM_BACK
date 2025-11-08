from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # bcrypt는 72바이트 초과 문자열을 지원하지 않음
    password = password[:72]
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool: # 비밀번호 검증 함수 추가
    return pwd_context.verify(plain_password, hashed_password)
