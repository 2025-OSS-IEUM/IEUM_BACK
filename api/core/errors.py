# api/core/errors.py

from fastapi import HTTPException


class APIException(HTTPException):
    """
    모든 API 오류를 표준 형식으로 반환하는 공통 예외 클래스.
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
    raise_error(ErrorCodes.XXX) 형태로 사용.
    내부적으로 APIException을 발생시킴.
    """
    error, status, message = code_tuple
    raise APIException(
        status_code=status,
        error=error,
        message=message
    )


class ErrorCodes:
    """
    모든 API 에러 코드 (ENUM-like)
    (error_code, http_status_code, message)
    """

    # ===============================
    # 🔐 인증 / 로그인
    # ===============================
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

    ERR_UNAUTHORIZED = (
        "ERR_UNAUTHORIZED",
        401,
        "인증 실패 또는 토큰 누락"
    )


    # ===============================
    # 🔧 비밀번호/코드 관련
    # ===============================
    PASSWORD_MISMATCH = (
        "PASSWORD_MISMATCH",
        400,
        "비밀번호와 비밀번호 확인이 일치하지 않습니다."
    )

    PASSWORD_POLICY_VIOLATION = (
        "PASSWORD_POLICY_VIOLATION",
        422,
        "비밀번호 형식이 보안 기준을 충족하지 않습니다."
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


    # ===============================
    # 🚨 제보(Reports) 관련 에러 코드 (Full Version)
    # ===============================

    # ❗ 동일 위치+타입 제보 중복
    REPORT_ALREADY_EXISTS = (
        "REPORT_ALREADY_EXISTS",
        409,
        "같은 위치에 동일한 유형의 제보가 이미 존재합니다."
    )

    # ❗ 제보 생성 실패
    REPORT_CREATE_FAILED = (
        "REPORT_CREATE_FAILED",
        500,
        "제보를 저장하는 중 오류가 발생했습니다."
    )

    # ❗ 제보 조회 실패
    REPORT_NOT_FOUND = (
        "REPORT_NOT_FOUND",
        404,
        "해당 제보를 찾을 수 없습니다."
    )

    # ❗ 제보 상태 변경 시 잘못된 입력
    REPORT_INVALID_STATUS = (
        "REPORT_INVALID_STATUS",
        400,
        "유효하지 않은 제보 상태(status) 값입니다."
    )

    # ❗ 이미 동일 상태로 업데이트 요청한 경우
    REPORT_STATUS_CONFLICT = (
        "REPORT_STATUS_CONFLICT",
        409,
        "이미 동일한 상태로 설정되어 있습니다."
    )

    # ❗ 권한 없는 사용자 접근
    REPORT_FORBIDDEN = (
        "REPORT_FORBIDDEN",
        403,
        "해당 제보에 대한 권한이 없습니다."
    )

    # ❗ 제보 삭제 권한 없음
    REPORT_DELETE_FORBIDDEN = (
        "REPORT_DELETE_FORBIDDEN",
        403,
        "제보를 삭제할 수 있는 권한이 없습니다."
    )

    # ❗ 제보 삭제 실패(DB)
    REPORT_DELETE_FAILED = (
        "REPORT_DELETE_FAILED",
        500,
        "제보 삭제 도중 서버 오류가 발생했습니다."
    )

    # ❗ 좌표 오류
    REPORT_INVALID_COORDINATES = (
        "REPORT_INVALID_COORDINATES",
        400,
        "좌표 형식이 잘못되었습니다."
    )


    # ===============================
    # 🗺 경로(Route) 관련
    # ===============================
    ROUTE_INVALID_COORDINATES = (
        "ROUTE_INVALID_COORDINATES",
        400,
        "출발지 또는 도착지 좌표가 올바르지 않습니다."
    )

    ROUTE_NOT_FOUND = (
        "ROUTE_NOT_FOUND",
        404,
        "요청한 지점 사이의 유효한 경로를 찾을 수 없습니다."
    )

    ROUTE_API_UNAVAILABLE = (
        "ROUTE_API_UNAVAILABLE",
        503,
        "외부 경로 API 응답 없음"
    )

    ROUTE_PARSE_FAILED = (
        "ROUTE_PARSE_FAILED",
        500,
        "경로 데이터를 처리하는 중 오류가 발생했습니다."
    )


    # ===============================
    # 📡 서버 / 시스템 공통
    # ===============================
    RATE_LIMIT_EXCEEDED = (
        "RATE_LIMIT_EXCEEDED",
        429,
        "요청 한도를 초과했습니다."
    )

    ERR_INVALID_REQUEST = (
        "ERR_INVALID_REQUEST",
        400,
        "요청 형식 또는 값이 잘못되었습니다."
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

    ERR_SERVER_FAILURE = (
        "ERR_SERVER_FAILURE",
        500,
        "서버 내부 오류입니다."
    )

    SERVICE_UNAVAILABLE = (
        "SERVICE_UNAVAILABLE",
        503,
        "서비스를 사용할 수 없습니다."
    )

    VALIDATION_ERROR = (
        "VALIDATION_ERROR",
        400,
        "입력 데이터 검증에 실패했습니다."
    )
