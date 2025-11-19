# api/routers/safe_route.py

from fastapi import APIRouter
from schemas.safe_route_schema import (
    SafeRouteRequest,
    SafeRouteResponse
)
from services.safe_route_service import attach_safety_info

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
