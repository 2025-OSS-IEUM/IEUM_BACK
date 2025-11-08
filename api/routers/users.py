from fastapi import APIRouter, HTTPException, status

# ===============================
#  🧩 Users Router (사용자 정보 관련)
# ===============================
# /users/me        : 내 프로필 조회
# /users/{user_id} : 특정 사용자 조회
# /users/delete    : 회원 탈퇴
#
# ⚙️ 구조 세팅 담당: 기본 로직 + 에러 코드 처리 포함
# ⚙️ 로직 담당: 이후 MongoDB, JWT 인증, 실제 DB 연동으로 확장 예정
# ===============================

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_my_profile():
    """
      내 프로필 정보 조회
    - JWT 인증 기반 사용자 정보 반환 예정
    - 인증 실패 시 401, 접근 제한 시 403 반환
    """
    try:
        # TODO: JWT 토큰 검증 로직 추가 예정
        is_authenticated = True
        is_active = True

        if not is_authenticated:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="인증이 필요합니다. 로그인 후 다시 시도하세요."
            )

        if not is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="비활성화된 계정입니다. 관리자에게 문의하세요."
            )

        # 정상 반환 예시 (임시 데이터)
        return {
            "user_id": "example_user",
            "nickname": "홍길동",
            "email": "user@example.com",
            "status": "active"
        }

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"내 프로필 조회 중 오류가 발생했습니다: {e}"
        )


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_by_id(user_id: str):
    """
      특정 사용자 정보 조회
    - 존재하지 않는 사용자일 경우 404 반환
    - 내부 서버 오류 발생 시 500 반환
    """
    try:
        # TODO: MongoDB에서 user_id 기반 조회 로직 추가
        dummy_user = {"id": "1234", "nickname": "테스트", "email": "test@example.com"}

        if user_id != "1234":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"사용자 {user_id} 정보를 찾을 수 없습니다."
            )

        return dummy_user

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"사용자 조회 중 오류가 발생했습니다: {e}"
        )


@router.delete("/delete", status_code=status.HTTP_200_OK)
async def delete_user():
    """
      회원 탈퇴 엔드포인트
    - 탈퇴 처리 성공 시 200 OK
    - 이미 탈퇴된 계정은 410 반환
    - 내부 DB 오류는 500 반환
    """
    try:
        # TODO: 실제 삭제 로직 추가 예정
        already_deleted = False
        db_error = False

        if already_deleted:
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="이미 탈퇴된 계정입니다."
            )

        if db_error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="데이터베이스 처리 중 오류가 발생했습니다."
            )

        return {"message": "계정이 성공적으로 삭제되었습니다."}

    except HTTPException as e:
        raise e

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회원 탈퇴 중 예기치 못한 오류가 발생했습니다: {e}"
        )
