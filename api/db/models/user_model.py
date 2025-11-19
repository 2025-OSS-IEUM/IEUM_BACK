# api/db/models/user_model.py

import uuid
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, Field

# --- API 명세 (1)의 'disabilityType' Enum ---
# 1단계 스키마(schemas/auth.py)와 동일하게 DB 모델에서도 정의합니다.
class DisabilityType(str, Enum):
    none = "none"
    blind = "blind"
    low_vision = "low_vision"
    hearing = "hearing"
    mobility = "mobility"
    cognitive = "cognitive"
    other = "other"

def generate_user_id():
    # API 명세 (1)의 응답 형식 'usr_...'
    return f"usr_{uuid.uuid4().hex[:12]}"

#
#    강의자료 02.들어가며.pdf (p.10)
#    'namedtuple'처럼 Pydantic 'BaseModel'도 
#    Mongo DB에 저장될 'User' 문서(Document)의 데이터 구조를 정의합니다.
class User(BaseModel):
    
    userId: str = Field(default_factory=generate_user_id)
    
    email: EmailStr
    username: str
    password_hash: str
    level: int = 1
    exp: int = 0
    
    # 강의자료 05.First-Class Functions.pdf (p.4, 7)
    # 'datetime.utcnow'는 '일급 함수(First-Class Function)'로
    # 'default_factory'의 인수로 사용됩니다.
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # API 명세 (1)의 'name' (Optional)
    name: str | None = None
    
    # API 명세 (1)의 'disability_type'
    disability_type: DisabilityType
    
    # 강의자료 04.데이터구조체-dictionary-sets.pdf (p.47)
    # "키 객체는 반드시 해시 가능해야 한다"
    # 이 모델을 Mongo DB에서 효율적으로 사용하려면, 
    # 'userId', 'username', 'email' 필드에 'unique index'를 생성해야 합니다.
    
    class Config:
        use_enum_values = True