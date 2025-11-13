from pydantic import BaseModel, Field, EmailStr, model_validator # (수정) model_validator 추가
from typing import Literal, Optional
from datetime import datetime
from bson import ObjectId # MongoDB의 고유 ID(_id) 타입
import re # (수정) 비밀번호 정책 검증을 위해 re 임포트

# (수업 자료 02) MongoDB의 ObjectId 타입을 Pydantic에서 사용하기 위한
# 특별한 유효성 검사 클래스 (그대로 사용하시면 됩니다)
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, *args, **kwargs): # (수정) Pydantic v2 호환을 위해 *args, **kwargs 추가
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema): # (수정) __modify_schema__ -> __get_pydantic_json_schema__
        field_schema.update(type="string")

# (API 명세서 1. (7) 접근성 설정 조회/변경)
# (수업 자료 04) 접근성 설정은 그 자체로 하나의 '딕셔너리' 구조입니다.
class AccessibilitySettings(BaseModel):
    ttsRate: float = Field(default=1.0, ge=0.5, le=1.5, description="음성 속도")
    ttsPitch: float = Field(default=1.0, ge=0.5, le=1.5, description="음성 높낮이")
    highContrast: bool = Field(default=False, description="고대비 모드")
    hapticFeedback: bool = Field(default=True, description="햅틱 피드백")
    voiceRepeat: Literal['short', 'normal', 'detailed'] = Field(default='normal', description="음성 안내 반복 수준")
    units: Literal['metric', 'imperial'] = Field(default='metric', description="단위")

# (API 명세서 1. (1) 회원 가입)
# 공통 필드를 UserBase로 분리
class UserBase(BaseModel):
    # Field(...)는 Pydantic을 사용한 유효성 검사입니다.
    username: str = Field(..., min_length=4, max_length=20, pattern="^[a-z0-9_]{4,20}$", description="사용자 아이디") # (수정) regex -> pattern
    email: EmailStr = Field(..., description="이메일 주소")
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="사용자 실명")
    disabilityType: Literal['none', 'blind', 'low_vision', 'hearing', 'mobility', 'cognitive', 'other'] = Field(..., description="장애 유형")

# 회원가입 시 Request Body로 받을 모델
class UserIn(UserBase):
    password: str = Field(..., description="비밀번호 원본")
    # (API 명세서 1. (1)의 passwordConfirm, consent는 
    #  API 로직 단(main.py)에서 검증하고 DB에는 저장하지 않습니다.)
    #  (이 모델을 1단계 스키마 SignupRequest 역할로 사용)


# MongoDB에 저장될 최종 모델 (DB 스키마 역할)
class UserInDB(UserBase):
    # (수업 자료 02) Pydantic 모델이 Python 데이터 모델을 활용하는 예시
    # MongoDB의 '_id' 필드를 Pydantic의 'id' 필드와 매핑
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str = Field(..., description="해시된 비밀번호")
    createdAt: datetime = Field(default_factory=datetime.now, description="가입일시") # (수정) utcnow -> now
    
    # (수업 자료 04) User 모델 내부에 AccessibilitySettings (딕셔너리) 모델을 중첩
    accessibility: AccessibilitySettings = Field(default_factory=AccessibilitySettings, description="개인 접근성 설정")

    class Config:
        json_encoders = {ObjectId: str} # ObjectId를 JSON으로 변환 가능하게
        arbitrary_types_allowed = True # PyObjectId 같은 커스텀 타입 허용
        populate_by_name = True # (수정) allow_population_by_field_name -> populate_by_name

# (API 명세서 1. (2) 로그인 요청)
# (1단계 스키마 LoginRequest 역할)
class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="로그인 이메일")
    password: str = Field(..., description="로그인 비밀번호")

# (API 명세서 1. (2) 로그인 응답 - 'user' 객체)
class UserInLoginResponse(BaseModel):
    # DB의 'id' (ObjectId)를 'userId' (문자열)로 변환하여 응답
    userId: str = Field(..., example="6551d7c7f766e2c606f3e7b2", description="앱 고유 ID") # (수정) userId 예시 변경
    username: str
    name: Optional[str]

# (API 명세서 1. (2) 로그인 응답 - 최종)
# (1단계 스키마 LoginResponse 역할)
class LoginResponse(BaseModel):
    accessToken: str = Field(..., example="eyJhbGciOiJIUzI1...")
    refreshToken: str = Field(..., example="def50200...")
    expiresIn: int = Field(..., example=3600)
    user: UserInLoginResponse

# (JWT 토큰 내부 Payload 정의)
class TokenPayload(BaseModel):
    sub: EmailStr # 'subject' (주체)로 email 사용

# --- [여기까지 로그인 관련 모델 추가] ---

print("✅ [api/models.py] User, Accessibility, Login 모델 로드 완료")

# --- (API 명세서 1. (17), (18) 중복 확인 응답) ---
class CheckAvailabilityResponse(BaseModel):
    available: bool
    message: Optional[str] = None
    
# --- (API 명세서 1. (3) 아이디 찾기) ---
class UsernameLookupRequest(BaseModel):
    email: EmailStr = Field(..., description="가입 시 사용한 이메일")

class UsernameLookupResponse(BaseModel):
    username: str = Field(..., description="조회된 사용자 아이디")
    
# --- (API 명세서 1. (4) 비밀번호 재설정 코드 발송) ---
class PasswordResetRequest(BaseModel):
    username: str = Field(..., description="코드를 받을 사용자의 아이디")

class PasswordResetResponse(BaseModel):
    # (수정) 00님의 모델에 맞게 message 필드 제거
    expiresIn: int = Field(..., description="인증 코드 유효 시간(초)")

# (5) 비밀번호 재설정 확정 ---
class PasswordResetConfirmRequest(BaseModel):
    username: str
    code: str
    newPassword: str
    newPasswordConfirm: str

    # Pydantic 모델 레벨에서 정책 검증 (API 명세서 422)
    @model_validator(mode='after')
    def validate_passwords(self) -> 'PasswordResetConfirmRequest':
        # 1. 비밀번호 일치 확인 (API 명세서 400)
        if self.newPassword != self.newPasswordConfirm:
            raise ValueError("비밀번호와 비밀번호 확인이 일치하지 않습니다.")
        
        # 2. 비밀번호 정책 확인 (API 명세서 422)
        pw = self.newPassword
        if len(pw) < 8:
            raise ValueError("비밀번호는 8자 이상이어야 합니다.")
        if not re.search(r"[!@#$%^&*(),.?:{}|<>]", pw):
            raise ValueError("비밀번호에 특수문자가 1개 이상 포함되어야 합니다.")
        
        return self

class PasswordResetConfirmResponse(BaseModel):
    message: str = "password reset successful"

print("✅ [api/models.py] 비밀번호 재설정 모델 로드 완료")