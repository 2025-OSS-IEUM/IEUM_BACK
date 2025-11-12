from pydantic import BaseModel, EmailStr, Field

# ===============================
#  Auth Schemas (회원 인증용)
# ===============================
# /auth/signup, /auth/login 요청·응답 데이터 구조 정의
# 구조 세팅 담당: 기본 스키마 정의 완료
# 로직 담당: 이후 실제 검증 및 JWT 토큰 발급 추가 예정
# ===============================


#  회원가입 요청
class SignupRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, example="ieum_user")
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., min_length=6, example="secure_password123")


#  회원가입 응답
class SignupResponse(BaseModel):
    user_id: str
    username: str
    email: EmailStr


#  로그인 요청
class LoginRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., min_length=6, example="secure_password123")


#  로그인 응답
class LoginResponse(BaseModel):
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = "bearer"
