from fastapi import APIRouter, HTTPException, status
from pydantic import EmailStr
import random
from datetime import datetime, timedelta, timezone
from pymongo.errors import DuplicateKeyError

# Models
from ..models import (
    UserIn, UserInDB,
    LoginRequest, LoginResponse, UserInLoginResponse,
    CheckAvailabilityResponse, UsernameLookupRequest, UsernameLookupResponse,
    PasswordResetRequest, PasswordResetResponse,
    PasswordResetConfirmRequest, PasswordResetConfirmResponse,
    ErrorResponse
)

from ..core import (
    users_collection,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

from ..core.security import (
    verify_password,
    hash_password,
    create_access_token,
    create_refresh_token
)

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


# -------------------------------------------------------
# 0. 상태 확인
# -------------------------------------------------------
@router.get("/status", status_code=status.HTTP_200_OK)
async def get_auth_status():
    return {"message": "Auth router active"}


# -------------------------------------------------------
# 1. 회원가입
# -------------------------------------------------------
@router.post("/signup",
             response_model=UserInDB,
             status_code=status.HTTP_201_CREATED)
async def signup(user_in: UserIn):

    # 0) 비밀번호 72바이트 체크
    if len(user_in.password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=422,
            detail=ErrorResponse(
                status=422,
                errorCode="PASSWORD_TOO_LONG",
                errorMessage="비밀번호는 최대 72바이트까지 가능합니다."
            ).model_dump()
        )

    # 1) 빠른 중복 체크
    if await users_collection.find_one({"username": user_in.username}):
        raise HTTPException(
            status_code=409,
            detail=ErrorResponse(
                status=409,
                errorCode="USERNAME_TAKEN",
                errorMessage="이미 사용 중인 아이디입니다."
            ).model_dump()
        )

    if await users_collection.find_one({"email": user_in.email}):
        raise HTTPException(
            status_code=409,
            detail=ErrorResponse(
                status=409,
                errorCode="EMAIL_TAKEN",
                errorMessage="이미 가입된 이메일 주소입니다."
            ).model_dump()
        )

    # 2) 해시 생성
    hashed_password = hash_password(user_in.password)
    user_data = user_in.model_dump(exclude={"password"})
    user_data["hashed_password"] = hashed_password
    new_user = UserInDB(**user_data)

    # 3) 삽입
    try:
        result = await users_collection.insert_one(new_user.model_dump(by_alias=True))
    except DuplicateKeyError as e:
        key = list(e.details.get("keyPattern", {}).keys())[0]
        code = "DUPLICATE_VALUE"
        message = "중복된 값이 있습니다."
        if key == "username":
            code = "USERNAME_TAKEN"
            message = "이미 사용 중인 아이디입니다."
        elif key == "email":
            code = "EMAIL_TAKEN"
            message = "이미 가입된 이메일 주소입니다."
        raise HTTPException(
            status_code=409,
            detail=ErrorResponse(
                status=409,
                errorCode=code,
                errorMessage=message
            ).model_dump()
        )

    # 4) 삽입 검증
    created_user = await users_collection.find_one({"_id": result.inserted_id})
    if not created_user:
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(
                status=500,
                errorCode="USER_CREATION_FAILED",
                errorMessage="사용자를 생성했으나 조회에 실패했습니다."
            ).model_dump()
        )

    return UserInDB(**created_user)


# -------------------------------------------------------
# 2. 로그인
# -------------------------------------------------------
@router.post("/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):

    user = await users_collection.find_one({"email": login_data.email})

    if not user or not verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=401,
            detail=ErrorResponse(
                status=401,
                errorCode="INVALID_CREDENTIALS",
                errorMessage="잘못된 이메일 또는 비밀번호입니다."
            ).model_dump(),
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

    return LoginResponse(
        accessToken=access_token,
        refreshToken=refresh_token,
        expiresIn=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_info
    )


# -------------------------------------------------------
# 3. 아이디 중복 확인
# -------------------------------------------------------
@router.get("/check-username", response_model=CheckAvailabilityResponse)
async def check_username_availability(username: str):
    exists = await users_collection.find_one({"username": username})
    if exists:
        return CheckAvailabilityResponse(
            available=False,
            message="이미 사용 중인 아이디입니다."
        )
    return CheckAvailabilityResponse(available=True)


# -------------------------------------------------------
# 4. 이메일 중복 확인
# -------------------------------------------------------
@router.get("/check-email", response_model=CheckAvailabilityResponse)
async def check_email_availability(email: EmailStr):
    exists = await users_collection.find_one({"email": email})
    if exists:
        return CheckAvailabilityResponse(
            available=False,
            message="이미 가입된 이메일입니다."
        )
    return CheckAvailabilityResponse(available=True)


# -------------------------------------------------------
# 5. 아이디 찾기
# -------------------------------------------------------
@router.post("/username/lookup", response_model=UsernameLookupResponse)
async def username_lookup(request: UsernameLookupRequest):
    user = await users_collection.find_one({"email": request.email})
    if not user:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                status=404,
                errorCode="USER_NOT_FOUND",
                errorMessage="해당 이메일로 등록된 계정이 없습니다."
            ).model_dump()
        )
    return UsernameLookupResponse(username=user["username"])


# -------------------------------------------------------
# 6. 비밀번호 재설정 코드 발송
# -------------------------------------------------------
@router.post("/password/reset", response_model=PasswordResetResponse)
async def request_password_reset(request: PasswordResetRequest):
    user = await users_collection.find_one({"username": request.username})
    if not user:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                status=404,
                errorCode="USER_NOT_FOUND",
                errorMessage="해당 아이디로 등록된 계정이 없습니다."
            ).model_dump()
        )

    reset_code = str(random.randint(100000, 999999))
    expires = 300
    expiry_time = datetime.now(timezone.utc) + timedelta(seconds=expires)

    await users_collection.update_one(
        {"username": request.username},
        {"$set": {
            "passwordResetCode": reset_code,
            "passwordResetExpires": expiry_time
        }}
    )

    print("=" * 50)
    print(f"[이메일 발송 시뮬레이션]")
    print(f"  수신자: {user['email']}")
    print(f"  인증코드: {reset_code} (유효시간: 5분)")
    print("=" * 50)

    return PasswordResetResponse(expiresIn=expires)


# -------------------------------------------------------
# 7. 비밀번호 재설정 확정
# -------------------------------------------------------
@router.post("/password/confirm", response_model=PasswordResetConfirmResponse)
async def confirm_password_reset(request: PasswordResetConfirmRequest):

    user = await users_collection.find_one({"username": request.username})
    if not user:
        raise HTTPException(
            status_code=404,
            detail=ErrorResponse(
                status=404,
                errorCode="USER_NOT_FOUND",
                errorMessage="해당 아이디로 등록된 계정이 없습니다."
            ).model_dump()
        )

    stored_code = user.get("passwordResetCode")
    expiry_time = user.get("passwordResetExpires")

    if not stored_code or stored_code != request.code:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                status=400,
                errorCode="INVALID_CODE",
                errorMessage="인증 코드가 유효하지 않습니다."
            ).model_dump()
        )

    if not expiry_time:
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                status=400,
                errorCode="CODE_EXPIRED",
                errorMessage="인증 코드의 유효 시간이 만료되었습니다."
            ).model_dump()
        )

    now_utc = datetime.now(timezone.utc)

    if expiry_time.tzinfo is None:
        expiry_time = expiry_time.replace(tzinfo=timezone.utc)

    if now_utc > expiry_time:
        await users_collection.update_one(
            {"username": request.username},
            {"$unset": {"passwordResetCode": "", "passwordResetExpires": ""}}
        )
        raise HTTPException(
            status_code=400,
            detail=ErrorResponse(
                status=400,
                errorCode="CODE_EXPIRED",
                errorMessage="인증 코드의 유효 시간이 만료되었습니다."
            ).model_dump()
        )

    # -----------------------------
    # 8) 비밀번호 72바이트 체크
    # -----------------------------
    if len(request.newPassword.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=422,
            detail=ErrorResponse(
                status=422,
                errorCode="PASSWORD_TOO_LONG",
                errorMessage="비밀번호는 최대 72바이트까지 가능합니다."
            ).model_dump()
        )

    # -----------------------------
    # 9) 새 비밀번호 해싱 및 DB 업데이트
    # -----------------------------
    hashed_password = hash_password(request.newPassword)

    await users_collection.update_one(
        {"username": request.username},
        {
            "$set": {"hashed_password": hashed_password},
            "$unset": {"passwordResetCode": "", "passwordResetExpires": ""}
        }
    )

    return PasswordResetConfirmResponse()
