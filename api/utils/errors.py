# api/utils/errors.py

from fastapi.responses import JSONResponse

def err(code: str, message: str, detail: str | None = None):
    """
    프로젝트 공통 에러 응답 포맷.
    
    Args:
        code (str): 에러 코드(ex: 'VALIDATION_ERROR')
        message (str): 사용자에게 보여줄 메세지
        detail (str | None): 디버깅용 상세 정보(선택)
    
    Returns:
        JSONResponse: FastAPI 표준 에러 응답
    """
    content = {
        "success": False,
        "error": {
            "code": code,
            "message": message
        }
    }

    if detail:
        content["error"]["detail"] = detail

    return JSONResponse(status_code=400, content=content)
