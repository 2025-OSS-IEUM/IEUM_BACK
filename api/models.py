# (수업 자료 02) Pydantic의 BaseModel은 파이썬 데이터 모델(특별 메서드)의
# 결정체이며, API의 데이터 형태(Schema)를 정의합니다.
from pydantic import BaseModel, Field, EmailStr
from typing import Literal, Optional
from datetime import datetime
from bson import ObjectId # MongoDB의 고유 ID(_id) 타입

# (수업 자료 02) MongoDB의 ObjectId 타입을 Pydantic에서 사용하기 위한
# 특별한 유효성 검사 클래스 (그대로 사용하시면 됩니다)
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
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
    username: str = Field(..., min_length=4, max_length=20, regex="^[a-z0-9_]{4,20}$", description="사용자 아이디")
    email: EmailStr = Field(..., description="이메일 주소")
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="사용자 실명")
    disabilityType: Literal['none', 'blind', 'low_vision', 'hearing', 'mobility', 'cognitive', 'other'] = Field(..., description="장애 유형")

# 회원가입 시 Request Body로 받을 모델
class UserIn(UserBase):
    password: str = Field(..., description="비밀번호 원본")
    # passwordConfirm, consent 등은 API 로직에서 처리하고 DB에 저장 X

# MongoDB에 저장될 최종 모델 (DB 스키마 역할)
class UserInDB(UserBase):
    # (수업 자료 02) Pydantic 모델이 Python 데이터 모델을 활용하는 예시
    # MongoDB의 '_id' 필드를 Pydantic의 'id' 필드와 매핑
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str = Field(..., description="해시된 비밀번호")
    createdAt: datetime = Field(default_factory=datetime.utcnow, description="가입일시")
    
    # (수업 자료 04) User 모델 내부에 AccessibilitySettings (딕셔너리) 모델을 중첩
    accessibility: AccessibilitySettings = Field(default_factory=AccessibilitySettings, description="개인 접근성 설정")

    class Config:
        json_encoders = {ObjectId: str} # ObjectId를 JSON으로 변환 가능하게
        arbitrary_types_allowed = True # PyObjectId 같은 커스텀 타입 허용
        allow_population_by_field_name = True # '_id'로도 'id' 필드 채우기 허용

print("✅ [api/models.py] User, Accessibility 모델 로드 완료")