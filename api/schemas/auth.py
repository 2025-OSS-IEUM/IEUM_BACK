# api/schemas/auth.py

from pydantic import BaseModel, EmailStr, Field, validator, model_validator
from datetime import datetime
from enum import Enum


# ===============================
#  Auth Schemas (회원 인증용)
# ===============================

class DisabilityType(str, Enum):
    none = "none"
    blind = "blind"
    low_vision = "low_vision"
    hearing = "hearing"
    mobility = "mobility"
    cognitive = "cognitive"
    other = "other"


class ConsentCreate(BaseModel):
    terms: bool
    privacy: bool

    @validator('terms', 'privacy')
    def must_be_true(cls, v):
        if v is not True:
            raise ValueError("약관에 동의해야 합니다.")
        return v


class SignupRequest(BaseModel):
    username: str = Field(..., min_length=4, max_length=20)
    email: EmailStr

    password: str = Field(..., min_length=8)
    passwordConfirm: str

    phone: str = Field(..., min_length=11, max_length=11)

    name: str | None = Field(default=None, min_length=1, max_length=50)
    disabilityType: DisabilityType
    consent: ConsentCreate

    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.password != self.passwordConfirm:
            raise ValueError("비밀번호와 비밀번호 확인이 일치하지 않습니다.")
        return self


class SignupResponse(BaseModel):
    user_id: str
    username: str
    email: EmailStr
    phone: str
    name: str | None
    disabilityType: DisabilityType
    createdAt: datetime


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=4, max_length=20)
    password: str = Field(..., min_length=6)


class UserInLoginResponse(BaseModel):
    user_id: str
    username: str
    name: str | None


class LoginResponse(BaseModel):
    accessToken: str
    token_type: str = "bearer"
    refreshToken: str
    expiresIn: int
    user: UserInLoginResponse


class TokenPayload(BaseModel):
    sub: EmailStr  # email


class UserInDB(BaseModel):
    user_id : str
    username: str
    email: EmailStr
    phone: str
    password_hash: str
    name: str | None = None
    disabilityType: DisabilityType
    createdAt: datetime = Field(default_factory=datetime.now)
    updatedAt: datetime = Field(default_factory=datetime.now)
    is_active: bool = True


class CheckAvailabilityResponse(BaseModel):
    available: bool
    message: str | None = None


class UsernameLookupRequest(BaseModel):
    email: EmailStr


class UsernameLookupResponse(BaseModel):
    username: str


class PasswordResetRequest(BaseModel):
    username: str


class PasswordResetResponse(BaseModel):
    expiresIn: int


class PasswordResetConfirmRequest(BaseModel):
    username: str
    code: str
    newPassword: str = Field(..., min_length=8)
    newPasswordConfirm: str

    @model_validator(mode='after')
    def check_passwords_match(self):
        if self.newPassword != self.newPasswordConfirm:
            raise ValueError("새 비밀번호와 비밀번호 확인이 일치하지 않습니다.")
        return self


class PasswordResetConfirmResponse(BaseModel):
    message: str = "비밀번호가 성공적으로 재설정되었습니다."
