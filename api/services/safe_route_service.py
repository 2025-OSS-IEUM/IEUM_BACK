# api/services/safe_route_service.py

from typing import List, Dict, Any, Tuple
from schemas.safe_route_schema import (
    SafeRouteOption,
    SafeRouteSegment,
    SafeRouteResponse
)
from db.database import find_hazards_near_coordinates
import math
from core.config import HAZARD_WEIGHTS, SEVERITY_WEIGHTS


# ---------------------------------------
# 1) 개별 지점 위험도 계산
# ---------------------------------------
async def compute_risk_for_point(point: Dict[str, float]) -> float:
    lon = point["lon"]
    lat = point["lat"]
    
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

    return math.exp(total) - 1


# ---------------------------------------
# 2) 경로 전체 점수 계산
# ---------------------------------------
async def compute_scores_for_path(path: List[Dict[str, float]]) -> Tuple[float, List[float]]:
    point_risk_scores = []
    total_risk_score = 0.0

    for point in path:
        risk = await compute_risk_for_point(point)
        point_risk_scores.append(risk)
        total_risk_score += risk

    final_safety_score = max(0, 100 - total_risk_score)

    return final_safety_score, point_risk_scores


# ---------------------------------------
# 3) 전체 경로 후보들에 대해 안전 점수 생성
# ---------------------------------------
async def attach_safety_info(route_candidates: List[Dict[str, Any]]) -> SafeRouteResponse:

    safe_routes: List[SafeRouteOption] = []
    best_score = -1
    best_index = 0

    for idx, route in enumerate(route_candidates):

        # (1) 경로 전체 점수 + 개별 점수
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

    # (5) 반환: SafeRouteResponse 객체
    return SafeRouteResponse(
        routes=safe_routes,
        bestRouteIndex=best_index
    )
