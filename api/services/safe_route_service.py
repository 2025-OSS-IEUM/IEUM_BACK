# api/services/safe_route_service.py

from typing import List, Dict, Any
from schemas.safe_route_schema import (
    SafeRouteOption,
    SafeRouteSegment,
    SafeRouteResponse
)


async def compute_safety_score_for_path(path: List[Dict[str, float]]) -> float:
    """
    TODO:
    - hazard DB 조회
    - 각 hazard까지 거리 계산
    - 위험도 가중치 계산
    - 최종 안전 점수 산출

    현재는 placeholder.
    """
    return 0.0


async def attach_safety_info(route_candidates: List[Dict[str, Any]]) -> SafeRouteResponse:
    """
    TODO:
    - C단계의 route 후보들에 대해 hazard 기반 안전 점수 붙이기
    - 각 경로 별 SafeRouteOption 생성

    route_candidates 형식 예시:
    [
        {
            "distance": float,
            "duration": float,
            "path": [
                {"lat": float, "lon": float},
                ...
            ]
        },
        ...
    ]
    """

    safe_routes: List[SafeRouteOption] = []

    for route in route_candidates:

        # TODO: 위험도 계산 함수 호출
        score = await compute_safety_score_for_path(route["path"])

        # TODO: 각 포인트별 riskScore도 나중에 계산
        segments = [
            SafeRouteSegment(
                lat=p["lat"],
                lon=p["lon"],
                riskScore=None
            )
            for p in route["path"]
        ]

        safe_route = SafeRouteOption(
            distance=route["distance"],
            duration=route["duration"],
            safetyScore=score,
            path=segments
        )

        safe_routes.append(safe_route)

    # TODO: 실제로 가장 안전한 경로를 비교해 index 도출
    best_index = 0

    return SafeRouteResponse(
        routes=safe_routes,
        bestRouteIndex=best_index
    )
