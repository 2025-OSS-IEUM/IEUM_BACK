from fastapi import APIRouter, HTTPException, status

# ===============================
#  🧩 Auth Router (회원 인증 관련)
# ===============================
# /auth/signup  : 회원가입
# /auth/login   : 로그인
# /auth/status  : 서버 연결 확인
#
# 구조 세팅 담당 : 기본 구조 및 오류 코드 세팅 완료
# 로직 담당 : 이후 MongoDB, JWT, 검증 로직 추가 예정
# ===============================

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.get("/status", status_code=status.HTTP_200_OK)
async def get_auth_status():
    """
      Auth 라우터 연결 상태 확인용
    - /auth/status
    - 서버와 라우터가 정상적으로 연결되어 있는지 확인합니다.
    """
    return {"message": "Auth router active"}


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup():
    """
      회원가입 엔드포인트
    - (A-1 단계) 사용자 데이터 검증 및 MongoDB 저장 로직 추가 예정
    - 요청 검증 실패 시 400 / 422, 중복 시 409, 내부 오류 시 500 반환 예정
    """
    try:
        # TODO: 요청 데이터 검증, 중복 확인, 비밀번호 해시, DB 저장
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="회원가입 기능이 아직 활성화되지 않았습니다. (개발 중)"
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"회원가입 처리 중 서버 오류가 발생했습니다: {e}"
        )


@router.post("/login", status_code=status.HTTP_200_OK)
async def login():
    """
      로그인 엔드포인트
    - (A-1 단계) 비밀번호 검증 및 JWT 발급 로직 추가 예정
    - 인증 실패 시 401, 비활성 계정 시 403, 서버 오류 시 500 반환 예정
    """
    try:
        # TODO: 사용자 조회, 비밀번호 검증, JWT 토큰 생성
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="로그인 기능이 아직 활성화되지 않았습니다. (개발 중)"
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"로그인 처리 중 서버 오류가 발생했습니다: {e}"
        )
