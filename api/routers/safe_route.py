# api/routers/safe_route.py

from fastapi import APIRouter
from schemas.safe_route_schema import (
    SafeRouteRequest,
    SafeRouteResponse,
    RerouteRequest  # [NEW] 스키마 추가
)
from services.safe_route_service import (
    attach_safety_info, 
    get_reroute_path # [NEW] 서비스 함수 추가 (서비스 파일에 구현 필요)
)

router = APIRouter(
    prefix="/routes",
    tags=["Routes"]
)

@router.post("/safe", response_model=SafeRouteResponse)
async def get_safe_route_with_scores(body: SafeRouteRequest):
    """
    C 단계에서 나온 RouteResponse(JSON):
    {
        "routes": [
            { "distance": ..., "duration": ..., "path": [...] },
            ...
        ]
    }
    
    이 구조 그대로 입력받아,
    D/E 단계에서 hazard 기반 안전 점수를 계산하고
    최종 SafeRouteResponse를 반환합니다.
    """

    # SafeRouteRequest → Python dict 변환
    # r.dict() : InputRoute
    route_candidates = [r.dict() for r in body.routes]

    # 위험도 계산 + bestRouteIndex 산출
    safe_route_response = await attach_safety_info(route_candidates)

    return safe_route_response


# -----------------------------------------------------------
# [NEW] 재탐색 API 추가
# -----------------------------------------------------------
@router.post("/reroute", response_model=SafeRouteResponse)
async def re_calculate_route(body: RerouteRequest):
    """
    [재탐색 기능]
    사용자 이탈 시, 현재 좌표(current)와 목적지(dest)를 받아
    새로운 경로를 탐색하고 안전 점수를 포함하여 반환합니다.
    """
    # 서비스 계층에서 '카카오/T맵 경로 찾기' -> '안전 점수 계산(attach_safety_info)' 과정을 수행
    reroute_response = await get_reroute_path(body)
    
    return reroute_response