from fastapi import APIRouter, HTTPException, status
from pydantic import EmailStr
import random
from datetime import datetime, timedelta, timezone

# 1. 의존성(Models) 가져오기
# 1. 의존성(Models) 가져오기
# (schemas/user.py 에는 UserIn이 없으므로, auth.py에서 모두 가져옵니다)
from schemas.auth import (
    SignupRequest, UserInDB,
    LoginRequest, LoginResponse, UserInLoginResponse,
    CheckAvailabilityResponse, UsernameLookupRequest, UsernameLookupResponse,
    PasswordResetRequest, PasswordResetResponse,
    PasswordResetConfirmRequest, PasswordResetConfirmResponse
)

from db.database import users_collection
# (core/config.py 에서 설정값(settings)을 가져옵니다)
from core.config import settings

from core.security import (
    verify_password, 
    hash_password, 
    create_access_token, 
    create_refresh_token
)

router = APIRouter(
    prefix="/auth", # 이 파일의 모든 경로는 /auth 로 시작
    tags=["Auth"]   # API 문서에서 "Auth" 태그로 그룹화
)

@router.get("/status", status_code=status.HTTP_200_OK)
async def get_auth_status():
    """Auth 라우터 연결 상태 확인용"""
    return {"message": "Auth router active"}

@router.post(
    "/signup",
    response_model=UserInDB,
    status_code=status.HTTP_201_CREATED
)
async def signup(user_in: SignupRequest):

    # 1) 아이디 / 이메일 중복 확인
    if await users_collection.find_one({"username": user_in.username}):
        raise HTTPException(409, "이미 사용 중인 아이디입니다.")
    if await users_collection.find_one({"email": user_in.email}):
        raise HTTPException(409, "이미 가입된 이메일 주소입니다.")

    # 2) 비밀번호 해싱
    hashed_password = hash_password(user_in.password)

    # 3) SignupRequest → DB 저장용 데이터로 매핑(clean)
    user_data = {
        "username": user_in.username,
        "email": user_in.email,

        # passwordConfirm, consent는 저장 ❌ → 버림
        "hashed_password": hashed_password,

        "name": user_in.name,
        "disabilityType": user_in.disabilityType,   # camelCase 그대로 저장해도 됨

        # UserInDB와 일치하도록 필드 생성
        "createdAt": datetime.now(),
        "updatedAt": datetime.now(),
        "is_active": True
    }

    # 4) DB 스키마(UserInDB)에 맞게 모델 인스턴스 생성
    new_user = UserInDB(**user_data)

    # 5) MongoDB 저장
    result = await users_collection.insert_one(new_user.model_dump())
    created = await users_collection.find_one({"_id": result.inserted_id})

    # 6) UserInDB로 응답 직렬화
    return UserInDB(**created)
    
@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    """(API 명세서 1. (2) 로그인)"""
    # core.py의 users_collection 사용
    user = await users_collection.find_one({"email": login_data.email})

    if not user or not verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 이메일 또는 비밀번호입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload_data = {"sub": user["email"]}
    access_token = create_access_token(data=payload_data)
    refresh_token = create_refresh_token(data=payload_data)
    
    user_info = UserInLoginResponse(
        userId=str(user["_id"]),
        username=user["username"],
        name=user.get("name")
    )
    
    # core.py의 ACCESS_TOKEN_EXPIRE_MINUTES 설정값 사용
    return LoginResponse(
        accessToken=access_token,
        refreshToken=refresh_token,
        expiresIn=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_info
    )

@router.get("/check-username", response_model=CheckAvailabilityResponse)
async def check_username_availability(username: str):
    """(API 명세서 1. (17) 아이디 중복 확인)"""
    existing_user = await users_collection.find_one({"username": username})
    if existing_user:
        return CheckAvailabilityResponse(available=False, message="이미 사용 중인 아이디입니다.")
    return CheckAvailabilityResponse(available=True)

@router.get("/check-email", response_model=CheckAvailabilityResponse)
async def check_email_availability(email: EmailStr):
    """(API 명세서 1. (18) 이메일 중복 확인)"""
    existing_email = await users_collection.find_one({"email": email})
    if existing_email:
        return CheckAvailabilityResponse(available=False, message="이미 가입된 이메일입니다.")
    return CheckAvailabilityResponse(available=True)

@router.post("/username/lookup", response_model=UsernameLookupResponse)
async def username_lookup(request: UsernameLookupRequest):
    """(API 명세서 1. (3) 아이디 찾기)"""
    user = await users_collection.find_one({"email": request.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found for the provided email address."
        )
    return UsernameLookupResponse(username=user["username"])

@router.post("/password/reset", response_model=PasswordResetResponse)
async def request_password_reset(request: PasswordResetRequest):
    """(API 명세서 1. (4) 비밀번호 재설정 코드 발송)"""
    user = await users_collection.find_one({"username": request.username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 아이디로 등록된 계정이 존재하지 않습니다."
        )

    reset_code = str(random.randint(100000, 999999))
    code_expires_in_seconds = 300 
    code_expiry_time = datetime.now(timezone.utc) + timedelta(seconds=code_expires_in_seconds)
    
    await users_collection.update_one(
        {"username": request.username},
        {"$set": {
            "passwordResetCode": reset_code,
            "passwordResetExpires": code_expiry_time
        }}
    )

    print("="*50)
    print(f"[이메일 발송 시뮬레이션]")
    print(f"  수신자: {user['email']}")
    print(f"  인증코드: {reset_code} (유효시간: 5분)")
    print("="*50)
    
    return PasswordResetResponse(expiresIn=code_expires_in_seconds)

@router.post("/password/confirm", response_model=PasswordResetConfirmResponse)
async def confirm_password_reset(request: PasswordResetConfirmRequest):
    """(API 명세서 1. (5) 비밀번호 재설정 확정)"""
    
    # 1. 사용자 찾기
    user = await users_collection.find_one({"username": request.username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 아이디로 등록된 계정이 존재하지 않습니다."
        )

    # 2. DB에 저장된 인증 코드 및 만료 시간 확인
    stored_code = user.get("passwordResetCode")
    expiry_time = user.get("passwordResetExpires")

    # 3. 인증 코드 일치 여부 확인
    if not stored_code or stored_code != request.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="인증 코드가 유효하지 않습니다."
        )
    
    # 4. 인증 코드 만료 여부 확인 (시간대 정보가 있는 현재 시간)
    if not expiry_time or datetime.now(timezone.utc) > expiry_time:
        # 만료된 코드는 DB에서 삭제
        await users_collection.update_one(
            {"username": request.username},
            {"$unset": {"passwordResetCode": "", "passwordResetExpires": ""}}
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="인증 코드의 유효 시간이 만료되었습니다."
        )

    # 5. 새 비밀번호 유효성 검사 (Pydantic)
    #    (models.py의 @model_validator가 자동으로 검사함)
    
    hashed_password = hash_password(request.newPassword)
    
    await users_collection.update_one(
        {"username": request.username},
        {
            "$set": {"hashed_password": hashed_password},
            "$unset": { # 비밀번호 변경에 성공했으므로 인증 코드 삭제
                "passwordResetCode": "",
                "passwordResetExpires": ""
            }
        }
    )

    # 7. 성공 응답 반환
    return PasswordResetConfirmResponse()