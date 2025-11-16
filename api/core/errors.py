# api/core/errors.py

######### 여기에 에러 코드를 전부 보관중입니다 / 필요하면 수정해서 써주세요 #########
######### 라우터 파일들에서 'raise_error(ErrorCodes.코드명)' 형태로 사용 #########

from fastapi import HTTPException

class APIException(HTTPException):
    """
    모든 API 오류를 표준화된 구조로 반환하는 커스텀 예외 클래스.
    - status: HTTP 상태 코드 (숫자)
    - error: 에러 코드 (영어, ENUM 형식)
    - message: 한국어 설명
    """
    def __init__(self, *, status_code: int, error: str, message: str):
        super().__init__(
            status_code=status_code,
            detail={
                "status": status_code,
                "error": error,
                "message": message
            }
        )


def raise_error(code_tuple):
    """
    오류 코드 튜플을 받아 APIException을 발생시키는 헬퍼 함수.
    사용:
        raise_error(ErrorCodes.USERNAME_NOT_FOUND)
    """
    error, status, message = code_tuple
    raise APIException(
        status_code=status,
        error=error,
        message=message
    )


class ErrorCodes:
    """
    모든 API 에러 코드를 관리하는 ENUM-like 클래스.
    (error_code, status_code, message)
    메시지는 한국어로 표기 가능.
    """

    # --- 회원가입 / 로그인 / 인증 ---
    USERNAME_NOT_FOUND = (
        "USERNAME_NOT_FOUND",
        404,
        "해당 아이디로 등록된 계정이 없습니다."
    )

    EMAIL_NOT_FOUND = (
        "EMAIL_NOT_FOUND",
        404,
        "해당 이메일로 등록된 계정이 없습니다."
    )

    EMAIL_ALREADY_EXISTS = (
        "EMAIL_ALREADY_EXISTS",
        409,
        "이미 사용 중인 이메일입니다."
    )

    USERNAME_ALREADY_EXISTS = (
        "USERNAME_ALREADY_EXISTS",
        409,
        "이미 사용 중인 아이디입니다."
    )

    INVALID_CREDENTIALS = (
        "INVALID_CREDENTIALS",
        401,
        "이메일 또는 비밀번호가 올바르지 않습니다."
    )

    USER_DISABLED = (
        "USER_DISABLED",
        403,
        "비활성화된 계정입니다."
    )


    # --- 비밀번호 재설정 ---
    PASSWORD_MISMATCH = (
        "PASSWORD_MISMATCH",
        400,
        "비밀번호와 비밀번호 확인이 일치하지 않습니다."
    )

    PASSWORD_POLICY_VIOLATION = (
        "PASSWORD_POLICY_VIOLATION",
        422,
        "비밀번호가 보안 규칙을 충족하지 않습니다. 형식을 다시 확인해주세요."
    )

    CODE_INVALID = (
        "CODE_INVALID",
        400,
        "인증 코드가 올바르지 않습니다."
    )

    CODE_EXPIRED = (
        "CODE_EXPIRED",
        410,
        "인증 코드가 만료되었습니다."
    )


    # --- 요청 한도 / 서버 관련 ---
    RATE_LIMIT_EXCEEDED = (
        "RATE_LIMIT_EXCEEDED",
        429,
        "요청 한도를 초과했습니다. 잠시 후 다시 시도해주세요."
    )

    SERVER_ERROR = (
        "SERVER_ERROR",
        500,
        "서버 내부 오류가 발생했습니다."
    )

    # --- 제보 관련 ---
    REPORT_ALREADY_EXISTS = (
        "REPORT_ALREADY_EXISTS",
        409,
        "해당 위치와 유형의 제보가 이미 존재합니다."
    )

