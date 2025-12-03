from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordBearer
from core.errors import ErrorCodes, raise_error
from core.security import verify_token
from db.database import reports_collection, users_collection  # users_collection 추가

# 토큰을 추출하기 위한 스키마 정의 (Authorization 헤더 체크용)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# ======================================
# 📌 GET /users/me — 내 프로필 조회 (임시)
# ======================================
@router.get("/me", status_code=status.HTTP_200_OK)
async def get_my_profile():
    """
    내 프로필 정보 조회 (임시 반환)
    """
    return {
        "user_id": "example_user",
        "username": "홍길동",
        "email": "user@example.com",
        "status": "active"
    }


# ======================================
# 📌 GET /users/{user_id} — 특정 사용자 조회 (임시)
# ======================================
@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_by_id(user_id: str):
    """
    특정 사용자 정보 조회 (임시)
    """
    dummy_user = {"id": "1234", "username": "테스트", "email": "test@example.com"}

    if user_id != "1234":
        raise_error(ErrorCodes.USERNAME_NOT_FOUND)

    return dummy_user


# ======================================
# 📌 DELETE /users/delete — 회원 탈퇴 (임시)
# ======================================
@router.delete("/delete", status_code=status.HTTP_200_OK)
async def delete_user():
    """
    회원 탈퇴 (임시)
    """
    already_deleted = False
    db_error = False

    if already_deleted:
        raise_error(ErrorCodes.USER_DISABLED)

    if db_error:
        raise_error(ErrorCodes.SERVER_ERROR)

    return {"message": "계정이 성공적으로 삭제되었습니다."}


# ======================================
# 📌 GET /users/me/reports — 내가 제보한 report 조회
# ======================================

@router.get("/me/reports", status_code=status.HTTP_200_OK)
async def get_my_reports(current_user = Depends(verify_token)):
    """
    내가 제보한 모든 report 조회
    - 전역 BearerAuth 기반
    - verify_token으로 이미 인증 완료됨
    """

    # verify_token → {"sub": username, "user_id": ...}
    username = current_user["sub"]

    # DB에서 user_id 가져오기
    user = await users_collection.find_one({"username": username}, {"user_id": 1})
    if not user:
        raise_error(ErrorCodes.USERNAME_NOT_FOUND)

    user_id = user["user_id"]

    # 본인 report 조회
    docs = await reports_collection.find({"user_id": user_id}).to_list(length=None)

    # ObjectId → 문자열 변환
    for r in docs:
        if "_id" in r:
            r["id"] = str(r.pop("_id"))

    return docs
