# api/schemas/safe_route_schema.py

from pydantic import BaseModel
from typing import List, Optional


class SafeRouteSegment(BaseModel):
    lat: float
    lon: float
    riskScore: Optional[float] = None
    # TODO: D단계에서 hazard DB 기반 위험도 값을 넣어줄 예정


class SafeRouteOption(BaseModel):
    distance: float
    duration: float
    safetyScore: float  # TODO: D단계에서 계산된 종합 안전 점수
    path: List[SafeRouteSegment]


class SafeRouteResponse(BaseModel):
    routes: List[SafeRouteOption]
    bestRouteIndex: int  # TODO: 가장 안전한 경로 index 계산 예정
