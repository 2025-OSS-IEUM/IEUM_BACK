from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

# ===============================
#  User Schemas (사용자 데이터용)
# ===============================
# /users/me, /users/{id}, /users/delete 관련 요청·응답 구조 정의
#
# 구조 세팅 담당 : 데이터 스키마 정의
# 로직 담당 : 이후 DB 연동 및 JWT 인증 로직 추가 예정
# ===============================


class UserBase(BaseModel):
    username: str = Field(..., example="ieum_user")
    email: EmailStr = Field(..., example="user@example.com")
    name: Optional[str] = Field(None, example="홍길동")


class UserProfile(BaseModel):
    id: str
    username: str
    email: EmailStr
    name: Optional[str]
    created_at: datetime
    is_active: bool = True


class UserUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None


class UserDeleteResponse(BaseModel):
    message: str = Field(..., example="계정이 성공적으로 삭제되었습니다.")
