from pydantic import BaseModel, Field, EmailStr, model_validator, ConfigDict
from typing import Literal, Optional
from datetime import datetime, timezone
from bson import ObjectId
import re


# -------------------------------------------------------
# 0. Pydantic에서 ObjectId 인식시키기
# -------------------------------------------------------
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str):
            return ObjectId(v)
        raise TypeError("ObjectId must be a string or ObjectId instance")


# -------------------------------------------------------
# 1. 공통 에러 응답
# -------------------------------------------------------
class ErrorResponse(BaseModel):
    status: int = Field(..., example=400)
    errorCode: str = Field(..., example="BAD_REQUEST")
    errorMessage: str = Field(..., example="요청 형식이 잘못되었습니다.")


# -------------------------------------------------------
# 2. 접근성 설정 (API 명세서 1-(7))
# -------------------------------------------------------
class AccessibilitySettings(BaseModel):
    ttsRate: float = Field(default=1.0, ge=0.5, le=1.5)
    ttsPitch: float = Field(default=1.0, ge=0.5, le=1.5)
    highContrast: bool = Field(default=False)
    hapticFeedback: bool = Field(default=True)
    voiceRepeat: Literal["short", "normal", "detailed"] = "normal"
    units: Literal["metric", "imperial"] = "metric"


# -------------------------------------------------------
# 3. 회원 공통 정보
# -------------------------------------------------------
class UserBase(BaseModel):
    username: str = Field(
        ...,
        min_length=4,
        max_length=20,
        pattern="^[a-z0-9_]{4,20}$"
    )
    email: EmailStr
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    disabilityType: Literal[
        "none", "blind", "low_vision", "hearing", "mobility", "cognitive", "other"
    ]


class UserIn(UserBase):
    password: str


# -------------------------------------------------------
# 4. MongoDB 저장 모델 (DB 스키마)
# -------------------------------------------------------
class UserInDB(UserBase):
    id: str = Field(default=None, alias="_id")  # 👈 여기 바뀜!
    hashed_password: str
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    accessibility: AccessibilitySettings = Field(default_factory=AccessibilitySettings)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={
            ObjectId: str,      # ObjectId → string 자동 변환
            datetime: lambda v: v.isoformat(),
        }
    )


# -------------------------------------------------------
# 5. 회원가입 응답 모델 (비밀번호 제거)
# -------------------------------------------------------
class UserSignupResponse(BaseModel):
    userId: str
    username: str
    email: EmailStr
    name: Optional[str]
    disabilityType: str
    createdAt: datetime
    accessibility: AccessibilitySettings


# -------------------------------------------------------
# 6. 로그인 (API 명세서 1-(2))
# -------------------------------------------------------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserInLoginResponse(BaseModel):
    userId: str
    username: str
    name: Optional[str]


class LoginResponse(BaseModel):
    accessToken: str
    refreshToken: str
    expiresIn: int
    user: UserInLoginResponse


# -------------------------------------------------------
# 7. JWT Payload
# -------------------------------------------------------
class TokenPayload(BaseModel):
    sub: EmailStr


# -------------------------------------------------------
# 8. 중복 확인 응답 (17), (18)
# -------------------------------------------------------
class CheckAvailabilityResponse(BaseModel):
    available: bool
    message: Optional[str] = None


# -------------------------------------------------------
# 9. 아이디 찾기 (3)
# -------------------------------------------------------
class UsernameLookupRequest(BaseModel):
    email: EmailStr


class UsernameLookupResponse(BaseModel):
    username: str


# -------------------------------------------------------
# 10. 비밀번호 재설정 코드 발송 (4)
# -------------------------------------------------------
class PasswordResetRequest(BaseModel):
    username: str


class PasswordResetResponse(BaseModel):
    expiresIn: int


# -------------------------------------------------------
# 11. 비밀번호 재설정 확정 (5)
# -------------------------------------------------------
class PasswordResetConfirmRequest(BaseModel):
    username: str
    code: str
    newPassword: str
    newPasswordConfirm: str

    @model_validator(mode="after")
    def validate_passwords(self):
        if self.newPassword != self.newPasswordConfirm:
            raise ValueError("비밀번호와 비밀번호 확인이 일치하지 않습니다.")

        pw = self.newPassword

        if len(pw) < 8:
            raise ValueError("비밀번호는 8자 이상이어야 합니다.")
        
        if not re.search(r"[!@#$%^&*(),.?:{}|<>]", pw):
            raise ValueError("비밀번호에 특수문자가 1개 이상 포함되어야 합니다.")

        return self


class PasswordResetConfirmResponse(BaseModel):
    message: str = "password reset successful"


print("✅ [api/models.py] 모든 모델이 정상적으로 로드되었습니다.")
