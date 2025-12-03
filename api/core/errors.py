# api/core/errors.py

from fastapi import HTTPException


class APIException(HTTPException):
    """
    모든 API 오류를 표준화된 구조로 반환하는 커스텀 예외 클래스.
    - status: HTTP 상태 코드
    - error: 에러 코드 문자열
    - message: 한국어 설명 메시지
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
    ErrorCodes.* 형태의 튜플을 받아 APIException을 발생시키는 헬퍼.
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
    """

    # ================================
    # 🔐 인증 / 회원 관련
    # ================================
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
        "아이디 또는 비밀번호가 올바르지 않습니다."
    )

    USER_DISABLED = (
        "USER_DISABLED",
        403,
        "비활성화된 계정입니다."
    )


    # ================================
    # 🔑 비밀번호 재설정
    # ================================
    PASSWORD_MISMATCH = (
        "PASSWORD_MISMATCH",
        400,
        "비밀번호와 비밀번호 확인이 일치하지 않습니다."
    )

    PASSWORD_POLICY_VIOLATION = (
        "PASSWORD_POLICY_VIOLATION",
        422,
        "비밀번호가 보안 규칙을 충족하지 않습니다."
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


    # ================================
    # ⚠ 서버 / 공통 오류
    # ================================
    SERVER_ERROR = (
        "SERVER_ERROR",
        500,
        "서버 내부 오류가 발생했습니다."
    )

    ERR_SERVER_FAILURE = (
        "ERR_SERVER_FAILURE",
        500,
        "서버 내부 처리 중 오류가 발생했습니다."
    )

    SERVICE_UNAVAILABLE = (
        "SERVICE_UNAVAILABLE",
        503,
        "현재 서버 또는 데이터베이스가 응답하지 않습니다."
    )

    RATE_LIMIT_EXCEEDED = (
        "RATE_LIMIT_EXCEEDED",
        429,
        "요청 한도를 초과했습니다."
    )

    VALIDATION_ERROR = (
        "VALIDATION_ERROR",
        400,
        "요청 값이 올바르지 않습니다."
    )

    ERR_UNAUTHORIZED = (
        "ERR_UNAUTHORIZED",
        401,
        "인증 실패 또는 토큰 누락"
    )

    ERR_INVALID_REQUEST = (
        "ERR_INVALID_REQUEST",
        400,
        "필드 누락 또는 잘못된 값입니다."
    )

    ERR_FORBIDDEN = (
        "ERR_FORBIDDEN",
        403,
        "권한이 없습니다."
    )

    ERR_NOT_FOUND = (
        "ERR_NOT_FOUND",
        404,
        "요청한 리소스를 찾을 수 없습니다."
    )

    ERR_CONFLICT = (
        "ERR_CONFLICT",
        409,
        "이미 동일 상태입니다."
    )


    # ================================
    # 🗺 제보(Report) 관련
    # ================================
    REPORT_ALREADY_EXISTS = (
        "REPORT_ALREADY_EXISTS",
        409,
        "해당 위치에 해결되지 않은 동일 제보가 이미 존재합니다."
    )


    # ================================
    # 🚗 경로(Route) 관련
    # ================================
    ROUTE_INVALID_COORDINATES = (
        "ROUTE_INVALID_COORDINATES",
        400,
        "출발지 또는 도착지 좌표가 올바르지 않습니다."
    )

    ROUTE_NOT_FOUND = (
        "ROUTE_NOT_FOUND",
        404,
        "요청한 좌표 사이에 유효한 경로가 없습니다."
    )

    ROUTE_API_UNAVAILABLE = (
        "ROUTE_API_UNAVAILABLE",
        503,
        "외부 경로 API 응답이 없습니다."
    )

    ROUTE_PARSE_FAILED = (
        "ROUTE_PARSE_FAILED",
        500,
        "경로 데이터를 처리하는 중 오류가 발생했습니다."
    )
