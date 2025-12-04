# api/services/safe_route_service.py

import asyncio  # 비동기 병렬 처리
import math
from typing import List, Dict, Any, Tuple

from schemas.safe_route_schema import (
    SafeRouteOption,
    SafeRouteSegment,
    SafeRouteResponse,
    RerouteRequest  # [NEW] 추가됨
)
from db.database import find_hazards_near_coordinates
from core.config import HAZARD_WEIGHTS, SEVERITY_WEIGHTS

# T맵 외부 경로 API 호출 함수 임포트
# (파일명/함수명은 현재 구조에 맞춰져 있습니다.)
from services.tmap_directions import get_directions
# ---------------------------------------
# 1) 개별 지점 위험도 계산
# ---------------------------------------
async def compute_risk_for_point(point: Dict[str, float]) -> float:
    lon = point["lon"]
    lat = point["lat"]
    
    # DB 조회 (I/O 바운드 작업)
    nearby_hazards = await find_hazards_near_coordinates(
        coordinates=[lon, lat],
        max_distance_meters=50
    )

    if not nearby_hazards:
        return 0.0

    total = 0.0
    for hazard in nearby_hazards:
        type_w = HAZARD_WEIGHTS.get(hazard.get("type"), 0.5)
        severity_w = SEVERITY_WEIGHTS.get(hazard.get("severity"), 1.0)
        total += type_w * severity_w

    # 위험도가 0이면 exp(0)-1 = 0
    return math.exp(total) - 1


# ---------------------------------------
# 2) 경로 전체 점수 계산 (병렬 처리)
# ---------------------------------------
async def compute_scores_for_path(path: List[Dict[str, float]]) -> Tuple[float, List[float]]:
    # 모든 점에 대한 계산 요청을 리스트(Tasks)로 만듦
    tasks = [compute_risk_for_point(point) for point in path]
    
    # 모든 Task 동시 실행
    point_risk_scores = await asyncio.gather(*tasks)
    
    total_risk_score = sum(point_risk_scores)
    final_safety_score = max(0, 100 - total_risk_score)

    return final_safety_score, list(point_risk_scores)


# ---------------------------------------
# 3) 전체 경로 후보들에 대해 안전 점수 생성
# ---------------------------------------
async def attach_safety_info(route_candidates: List[Dict[str, Any]]) -> SafeRouteResponse:
    """
    route_candidates 구조 예시:
    [
    { "distance": 500, "duration": 300, "path": [{"lat":37.1, "lon":127.1}, ...] },
    ...
    ]
    """
    safe_routes: List[SafeRouteOption] = []
    best_score = -float('inf')
    best_index = 0

    for idx, route in enumerate(route_candidates):
        # (1) 경로 전체 점수 + 개별 점수 (병렬 처리)
        score, segment_risks = await compute_scores_for_path(route["path"])

        # (2) 각 지점 segment 생성
        segments = [
            SafeRouteSegment(
                lat=p["lat"],
                lon=p["lon"],
                riskScore=r
            )
            for p, r in zip(route["path"], segment_risks)
        ]

        # (3) SafeRouteOption 생성
        option = SafeRouteOption(
            distance=route["distance"],
            duration=route["duration"],
            safetyScore=score,
            path=segments
        )

        safe_routes.append(option)

        # (4) 최적 경로 선정
        if score > best_score:
            best_score = score
            best_index = idx

    return SafeRouteResponse(
        routes=safe_routes,
        bestRouteIndex=best_index
    )


# ---------------------------------------
# 4) [NEW] 재탐색 기능 (최종 수정)
# ---------------------------------------
async def get_reroute_path(request: RerouteRequest) -> SafeRouteResponse:
    """
    사용자 이탈 시 현재 위치 -> 목적지 경로를 다시 찾고,
    기존 로직(attach_safety_info)을 재사용해 안전 점수를 매깁니다.
    """
    
    # 1. 외부 API 출하여 경로 데이터 획득
    # get_directions 함수는 List[Dict]를 반환하도록 수정되었으므로, 개별 인자로 호출합니다.
    route_candidates = await get_directions(
        request.current_lat, 
        request.current_lon,
        request.dest_lat,
        request.dest_lon
    )

    # 2. 기존 안전 점수 계산 로직 재사용
    # (route_candidates는 이미 List[Dict] 형태이므로 그대로 전달)
    response = await attach_safety_info(route_candidates)
    
    return response