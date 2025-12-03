from fastapi import APIRouter, status
from pydantic import EmailStr
import random
from datetime import datetime, timedelta, timezone
from bson import ObjectId

# Schemas
from schemas.auth import (
    SignupRequest, UserInDB,
    LoginRequest, LoginResponse, UserInLoginResponse,
    CheckAvailabilityResponse, UsernameLookupRequest, UsernameLookupResponse,
    PasswordResetRequest, PasswordResetResponse,
    PasswordResetConfirmRequest, PasswordResetConfirmResponse
)

# DB
from db.database import users_collection

# Settings / Security
from core.config import settings
from core.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token
)

# 에러 코드 통합
from core.errors import ErrorCodes, raise_error


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


# --------------------------------------------------------
# 상태 체크
# --------------------------------------------------------
@router.get("/status", status_code=status.HTTP_200_OK)
async def get_auth_status():
    return {"message": "Auth router active"}


# --------------------------------------------------------
# 회원가입
# --------------------------------------------------------
@router.post("/signup", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def signup(user_in: SignupRequest):

    # 아이디 중복
    if await users_collection.find_one({"username": user_in.username}):
        raise_error(ErrorCodes.USERNAME_ALREADY_EXISTS)

    # 이메일 중복
    if await users_collection.find_one({"email": user_in.email}):
        raise_error(ErrorCodes.EMAIL_ALREADY_EXISTS)

    # 비밀번호 해싱
    password_hash = hash_password(user_in.password)   # ✔ 통일된 필드명

    user_data = {
        "username": user_in.username,
        "email": user_in.email,
        "phone": user_in.phone,
        "password_hash": password_hash,               # ✔ 수정됨
        "name": user_in.name,
        "disabilityType": user_in.disabilityType,
        "createdAt": datetime.now(),
        "updatedAt": datetime.now(),
        "is_active": True,
        "user_id": str(ObjectId()),
    }

    new_user = UserInDB(**user_data)
    result = await users_collection.insert_one(new_user.model_dump())
    created = await users_collection.find_one({"_id": result.inserted_id})

    return UserInDB(**created)


# --------------------------------------------------------
# 로그인
# --------------------------------------------------------
@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):

    # 🔥 username 기준으로 조회
    user = await users_collection.find_one({"username": login_data.username})

    # ✔ password_hash로 통일되어 있으므로 이대로 두면 완벽함
    if not user or not verify_password(login_data.password, user["password_hash"]):
        raise_error(ErrorCodes.INVALID_CREDENTIALS)

    payload = {
        "sub": user["username"],
        "user_id": user["user_id"]
    }

    access_token = create_access_token(data=payload)
    refresh_token = create_refresh_token(data=payload)

    user_info = UserInLoginResponse(
        user_id=user["user_id"],
        username=user["username"],
        name=user.get("name")
    )

    return LoginResponse(
        accessToken=access_token,
        refreshToken=refresh_token,
        expiresIn=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_info
    )


# --------------------------------------------------------
# 아이디 중복 확인
# --------------------------------------------------------
@router.get("/check-username", response_model=CheckAvailabilityResponse)
async def check_username(username: str):

    if await users_collection.find_one({"username": username}):
        return CheckAvailabilityResponse(available=False, message="이미 사용 중인 아이디입니다.")

    return CheckAvailabilityResponse(available=True)


# --------------------------------------------------------
# 이메일 중복 확인
# --------------------------------------------------------
@router.get("/check-email", response_model=CheckAvailabilityResponse)
async def check_email(email: EmailStr):

    if await users_collection.find_one({"email": email}):
        return CheckAvailabilityResponse(available=False, message="이미 가입된 이메일입니다.")

    return CheckAvailabilityResponse(available=True)


# --------------------------------------------------------
# 아이디 찾기
# --------------------------------------------------------
@router.post("/username/lookup", response_model=UsernameLookupResponse)
async def username_lookup(request: UsernameLookupRequest):

    user = await users_collection.find_one({"email": request.email})
    if not user:
        raise_error(ErrorCodes.EMAIL_NOT_FOUND)

    return UsernameLookupResponse(username=user["username"])


# --------------------------------------------------------
# 비밀번호 재설정 코드 발송
# --------------------------------------------------------
@router.post("/password/reset", response_model=PasswordResetResponse)
async def request_password_reset(request: PasswordResetRequest):

    user = await users_collection.find_one({"username": request.username})
    if not user:
        raise_error(ErrorCodes.USERNAME_NOT_FOUND)

    reset_code = str(random.randint(100000, 999999))
    expires_in = 300
    expiry_time = datetime.now(timezone.utc) + timedelta(seconds=expires_in)

    await users_collection.update_one(
        {"username": request.username},
        {"$set": {
            "passwordResetCode": reset_code,
            "passwordResetExpires": expiry_time
        }}
    )

    print("="*50)
    print("[이메일 발송 시뮬레이션]")
    print(f"수신자: {user['email']}")
    print(f"인증코드: {reset_code} (유효시간 5분)")
    print("="*50)

    return PasswordResetResponse(expiresIn=expires_in)


# --------------------------------------------------------
# 비밀번호 재설정 확정
# --------------------------------------------------------
@router.post("/password/confirm", response_model=PasswordResetConfirmResponse)
async def confirm_password_reset(request: PasswordResetConfirmRequest):

    user = await users_collection.find_one({"username": request.username})
    if not user:
        raise_error(ErrorCodes.USERNAME_NOT_FOUND)

    stored_code = user.get("passwordResetCode")
    expiry_time = user.get("passwordResetExpires")

    # 🔥 MongoDB가 tzinfo를 지워버리는 경우 UTC로 강제 보정
    if expiry_time and expiry_time.tzinfo is None:
        expiry_time = expiry_time.replace(tzinfo=timezone.utc)

    if not stored_code or stored_code != request.code:
        raise_error(ErrorCodes.CODE_INVALID)

    if not expiry_time or datetime.now(timezone.utc) > expiry_time:
        await users_collection.update_one(
            {"username": request.username},
            {"$unset": {"passwordResetCode": "", "passwordResetExpires": ""}}
        )
        raise_error(ErrorCodes.CODE_EXPIRED)

    password_hash = hash_password(request.newPassword)

    # ✔ 여기서도 필드명 통일
    await users_collection.update_one(
        {"username": request.username},
        {
            "$set": {"password_hash": password_hash},   # ✔ 수정됨
            "$unset": {
                "passwordResetCode": "",
                "passwordResetExpires": ""
            }
        }
    )

    return PasswordResetConfirmResponse()
