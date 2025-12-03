from pydantic import BaseModel
from typing import List, Optional

# -------------------------
# 입력용 스키마 (E 단계 입력: 기존 경로 분석용)
# -------------------------

class InputPathPoint(BaseModel):
    lat: float
    lon: float


class InputRoute(BaseModel):
    distance: float
    duration: float
    path: List[InputPathPoint]


class SafeRouteRequest(BaseModel):
    routes: List[InputRoute]


# -------------------------
# [추가됨] 재탐색 요청 스키마 (현재 위치 -> 목적지)
# -------------------------

class RerouteRequest(BaseModel):
    current_lat: float  # 현재 위치 위도
    current_lon: float  # 현재 위치 경도
    dest_lat: float     # 목적지 위도
    dest_lon: float     # 목적지 경도


# -------------------------
# 출력용 스키마 (E 단계 응답: 재탐색 결과도 이 형식을 사용)
# -------------------------

class SafeRouteSegment(BaseModel):
    lat: float
    lon: float
    riskScore: Optional[float] = None


class SafeRouteOption(BaseModel):
    distance: float
    duration: float
    safetyScore: float
    path: List[SafeRouteSegment]


class SafeRouteResponse(BaseModel):
    routes: List[SafeRouteOption]
    bestRouteIndex: int