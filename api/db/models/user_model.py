from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class User(BaseModel):
    email: EmailStr
    username: str
    password_hash: str
    level: int = 1
    exp: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
