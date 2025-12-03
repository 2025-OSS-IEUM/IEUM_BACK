# api/services/safe_route_service.py

import asyncio  # [추가] 비동기 병렬 처리를 위해 필수
import math
from typing import List, Dict, Any, Tuple

from schemas.safe_route_schema import (
    SafeRouteOption,
    SafeRouteSegment,
    SafeRouteResponse
)
from db.database import find_hazards_near_coordinates
from core.config import HAZARD_WEIGHTS, SEVERITY_WEIGHTS

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
        # 안전한 조회를 위해 .get() 사용 (기본값 설정)
        type_w = HAZARD_WEIGHTS.get(hazard.get("type"), 0.5)
        severity_w = SEVERITY_WEIGHTS.get(hazard.get("severity"), 1.0)
        total += type_w * severity_w

    # 위험도가 0이면 exp(0)-1 = 0, 위험도가 높을수록 급격히 증가
    return math.exp(total) - 1


# ---------------------------------------
# 2) 경로 전체 점수 계산 (🚀 핵심 수정: 병렬 처리)
# ---------------------------------------
async def compute_scores_for_path(path: List[Dict[str, float]]) -> Tuple[float, List[float]]:
    
    # [수정 전] for 문을 돌며 하나씩 DB 조회 -> 점이 100개면 100번 순차 대기 (매우 느림)
    # [수정 후] 모든 점에 대한 계산 요청을 리스트(Tasks)로 만듦
    tasks = [compute_risk_for_point(point) for point in path]
    
    # asyncio.gather: 모든 Task를 동시에 실행하고 결과가 다 모일 때까지 기다림
    # 순차 실행 대비 속도가 획기적으로 빨라짐
    point_risk_scores = await asyncio.gather(*tasks)
    
    # 결과 합산
    total_risk_score = sum(point_risk_scores)

    final_safety_score = max(0, 100 - total_risk_score)

    # gather의 결과는 튜플이므로 리스트로 변환하여 반환
    return final_safety_score, list(point_risk_scores)


# ---------------------------------------
# 3) 전체 경로 후보들에 대해 안전 점수 생성
# ---------------------------------------
async def attach_safety_info(route_candidates: List[Dict[str, Any]]) -> SafeRouteResponse:

    safe_routes: List[SafeRouteOption] = []
    # 초기값은 가장 낮은 값으로 설정 (-1 혹은 음의 무한대)
    best_score = -float('inf')
    best_index = 0

    for idx, route in enumerate(route_candidates):

        # (1) 경로 전체 점수 + 개별 점수 (병렬 처리된 함수 호출)
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