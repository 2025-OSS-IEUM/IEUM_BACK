# api/services/cache.py
from typing import Any, Optional
import json

import redis.asyncio as redis
from core.config import settings


# Redis 클라이언트 (async)
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    encoding="utf-8",
    decode_responses=True,  # 문자열 자동 디코딩
)


async def get_cache(key: str) -> Optional[Any]:
    """캐시에서 값 조회"""
    data = await redis_client.get(key)
    if data is None:
        return None
    return json.loads(data)


async def set_cache(key: str, value: Any, ttl: int = 300) -> None:
    """캐시에 값 저장 (ttl: 초 단위)"""
    await redis_client.set(key, json.dumps(value, default=str), ex=ttl)