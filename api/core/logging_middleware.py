# api/core/logging_middleware.py
import time
import logging
from starlette.requests import Request
from starlette.responses import Response

# 기본 로거 설정
logger = logging.getLogger("ieum")
logger.setLevel(logging.INFO)

# 핸들러가 하나도 없으면(중복 방지)
if not logger.handlers:
    handler = logging.StreamHandler()  # 콘솔로 출력
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


async def logging_middleware(request: Request, call_next):
    start = time.time()
    response: Response = await call_next(request)
    duration = (time.time() - start) * 1000  # ms 단위

    logger.info(
        "%s %s -> %d (%.2f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )

    return response