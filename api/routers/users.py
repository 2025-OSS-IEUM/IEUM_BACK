from fastapi import APIRouter, status
from core.errors import ErrorCodes, raise_error

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# ======================================
# 📌 GET /users/me — 내 프로필 조회
# ======================================
@router.get("/me", status_code=status.HTTP_200_OK)
async def get_my_profile():
    """
    내 프로필 정보 조회
    - JWT 인증 로직 추가 예정
    - 인증 실패 시 401, 비활성 계정은 403 반환
    """

    # TODO: JWT 토큰 인증 + DB 조회 추가 예정
    is_authenticated = True
    is_active = True

    # 1) 인증 실패
    if not is_authenticated:
        raise_error(ErrorCodes.INVALID_CREDENTIALS)

    # 2) 비활성 계정
    if not is_active:
        raise_error(ErrorCodes.USER_DISABLED)

    # 3) 임시 정상 반환
    return {
        "user_id": "example_user",
        "username": "홍길동",
        "email": "user@example.com",
        "status": "active"
    }


# ======================================
# 📌 GET /users/{user_id} — 특정 사용자 조회
# ======================================
@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_by_id(user_id: str):
    """
    특정 사용자 정보 조회
    - 없는 경우 404
    """

    # TODO: MongoDB 조회 로직 추가
    dummy_user = {"id": "1234", "username": "테스트", "email": "test@example.com"}

    if user_id != "1234":
        raise_error(ErrorCodes.USERNAME_NOT_FOUND)

    return dummy_user


# ======================================
# 📌 DELETE /users/delete — 회원 탈퇴
# ======================================
@router.delete("/delete", status_code=status.HTTP_200_OK)
async def delete_user():
    """
    회원 탈퇴
    - 이미 탈퇴한 계정 → 410
    - DB 오류 → 500
    """

    # TODO: 실제 DB 업데이트/삭제 로직 연결 예정
    already_deleted = False
    db_error = False

    if already_deleted:
        raise_error(ErrorCodes.USER_DISABLED)

    if db_error:
        raise_error(ErrorCodes.SERVER_ERROR)

    return {"message": "계정이 성공적으로 삭제되었습니다."}
