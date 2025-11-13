# api/schemas/auth.py

from pydantic import BaseModel, EmailStr, Field, validator, model_validator
from datetime import datetime
from enum import Enum

# ===============================
#  Auth Schemas (회원 인증용)
# ===============================
# /auth/signup, /auth/login 요청·응답 데이터 구조 정의
# ===============================

# --- API 명세 (1)의 'disabilityType' Enum ---
class DisabilityType(str, Enum):
    none = "none"
    blind = "blind"
    low_vision = "low_vision"
    hearing = "hearing"
    mobility = "mobility"
    cognitive = "cognitive"
    other = "other"

# --- API 명세 (1)의 'consent' 모델 ---
# 강의자료 02.들어가며.pdf (p.10)
# [cite_start]'namedtuple'처럼 Pydantic 'BaseModel'도 데이터 구조를 정의합니다. [cite: 848, 1530]
class ConsentCreate(BaseModel):
    terms: bool
    privacy: bool

    @validator('terms', 'privacy')
    def must_be_true(cls, v):
        if v is not True:
            # API 명세 (1)의 'consent.terms/privacy (required): true' 규칙
            raise ValueError("약관에 동의해야 합니다.")
        return v

# --- 회원가입 요청 ---
class SignupRequest(BaseModel):
    
    # 강의자료 05.First-Class Functions.pdf (p.34)
    # [cite_start]함수 어노테이션('text:str')처럼 Pydantic 모델도 타입 어노테이션을 사용합니다. [cite: 2624]
    username: str = Field(
        ..., 
        min_length=4,  # API 명세서 기준
        max_length=20, 
        example="ieum_user01"
    )
    email: EmailStr = Field(..., example="user@example.com")
    
    # API 명세 (1)의 비밀번호 정규식 반영
    password: str = Field(
        ..., 
        min_length=8, # API 명세서 기준
        example="P@ssw0rd!"
    )
    # API 명세 (1)의 'passwordConfirm'
    passwordConfirm: str = Field(..., example="P@ssw0rd!")
    
    # API 명세 (1)의 'name' (Optional)
    name: str | None = Field(default=None, min_length=1, max_length=50, example="홍길동")
    
    # API 명세 (1)의 'disabilityType'
    disabilityType: DisabilityType
    
    # API 명세 (1)의 'consent'
    consent: ConsentCreate

    # 비밀번호 일치 검증 로직
    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.password != self.passwordConfirm:
            # API 명세 (Error Cases)의 'PASSWORD_MISMATCH'
            raise ValueError('비밀번호와 비밀번호 확인이 일치하지 않습니다.')
        return self


# --- 회원가입 응답 ---
class SignupResponse(BaseModel):
    user_id: str 
    username: str
    email: EmailStr
    
    # API 명세 (1)의 응답 필드
    name: str | None
    disabilityType: DisabilityType
    createdAt: datetime


# --- 로그인 요청 ---
class LoginRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., min_length=6, example="secure_password123")


# --- 로그인 응답의 'user' 객체 ---
# API 명세 (2)의 중첩된 'user' 객체 정의
class UserInLoginResponse(BaseModel):
    userId: str = Field(..., example="usr_01JXYZ...")
    username: str = Field(..., example="ieum_user01")
    name: str | None = Field(..., example="홍길동")


# --- 로그인 응답 ---
class LoginResponse(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = "bearer"
    
    # API 명세 (2)의 응답 필드
    refreshToken: str = Field(..., example="def50200...")
    expiresIn: int = Field(..., example=3600)
    user: UserInLoginResponse # 중첩된 객체 사용

# --- JWT 토큰 내부 정보 (Payload) ---
class TokenPayload(BaseModel):
    # 'sub' (subject)는 토큰의 주체를 나타냅니다.
    # 로그인 방식이 'email'이므로 sub도 'email'로 하는 것이 일관성 있습니다.
    sub: EmailStr # email

# --- DB 저장을 위한 UserInDB 모델 ---
class UserInDB(BaseModel):
    username: str
    email: EmailStr
    hashed_password: str # <-- 비밀번호가 해시되어 저장됨
    name: str | None = None
    disabilityType: DisabilityType
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)
    is_active: bool = True
    
# --- API 명세 (17) 아이디/이메일 중복 확인 응답 ---
class CheckAvailabilityResponse(BaseModel):
    available: bool
    message: str | None = None


# --- API 명세 (3) 아이디 찾기 요청 ---
class UsernameLookupRequest(BaseModel):
    email: EmailStr


# --- API 명세 (3) 아이디 찾기 응답 ---
class UsernameLookupResponse(BaseModel):
    username: str


# --- API 명세 (4) 비밀번호 재설정 코드 발송 요청 ---
class PasswordResetRequest(BaseModel):
    username: str


# --- API 명세 (4) 비밀번호 재설정 코드 발송 응답 ---
class PasswordResetResponse(BaseModel):
    expiresIn: int


# --- API 명세 (5) 비밀번호 재설정 확정 요청 ---
class PasswordResetConfirmRequest(BaseModel):
    username: str
    code: str
    newPassword: str = Field(..., min_string=8)
    newPasswordConfirm: str

    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.newPassword != self.newPasswordConfirm:
            raise ValueError('새 비밀번호와 비밀번호 확인이 일치하지 않습니다.')
        return self


# --- API 명세 (5) 비밀번호 재설정 확정 응답 ---
class PasswordResetConfirmResponse(BaseModel):
    message: str = "비밀번호가 성공적으로 재설정되었습니다."