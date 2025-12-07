from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional
from bson import ObjectId

# Pydantic V2 스타일로 조금 다듬었습니다 (V1이어도 class Config 사용 가능)
class MongoBaseModel(BaseModel):
    # V2에서는 model_config를 사용하지만, 호환성을 위해 기존 스타일 유지도 괜찮습니다.
    # 여기서는 범용적으로 쓰이는 방식으로 둡니다.
    class Config:
        populate_by_name = True # 구버전 allow_population_by_field_name 대체
        json_encoders = {ObjectId: str}

class UserBase(BaseModel):
    username: str = Field(..., example="ieum_user")
    email: EmailStr = Field(..., example="user@example.com")
    name: Optional[str] = Field(None, example="홍길동")


# ✔️ API 응답용 (user_id는 DB의 별도 필드)
class UserProfile(UserBase, MongoBaseModel):
    user_id: str = Field(..., example="ieum_123456")
    created_at: datetime
    is_active: bool = True


# ✔️ DB 저장/조회용 (id = _id, user_id = 문자열)
class UserInDB(UserBase, MongoBaseModel):
    id: Optional[str] = Field(None, alias="_id")   # DB ObjectId
    user_id: str                                   # 문자열 user_id
    hashed_password: str
    created_at: datetime
    is_active: bool = True


# ✔️ 회원 삭제 응답
class UserDeleteResponse(BaseModel):
    message: str = Field(..., example="계정이 성공적으로 삭제되었습니다.")