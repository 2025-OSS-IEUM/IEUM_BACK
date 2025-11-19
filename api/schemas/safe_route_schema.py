from pydantic import BaseModel
from typing import List, Optional

# -------------------------
# 입력용 스키마 (E 단계 입력)
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
# 출력용 스키마 (E 단계 응답)
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
