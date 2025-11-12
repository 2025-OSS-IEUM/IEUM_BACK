# app/utils/errors.py
from typing import Dict, Any

def err(code: str, message: str, details: Any | None = None) -> Dict[str, Any]:
    payload = {"error": {"code": code, "message": message}}
    if details is not None:
        payload["error"]["details"] = details
    return payload

# 예: err("VALIDATION_ERROR", "필수 필드 누락")
