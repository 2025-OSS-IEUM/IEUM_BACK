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


async def compute_risk_for_point(point: Dict[str, float]) -> float:
    """
    [새로 추가된 헬퍼 함수]
    단일 지점(point)의 위험 요소를 조회하고
    exp(risk) - 1 값을 반환합니다.
    """
    lon = point["lon"]
    lat = point["lat"]
    
    # 1. DB에서 이 지점 주변 위험요소 조회
    nearby_hazards = await find_hazards_near_coordinates(
        coordinates=[lon, lat], 
        max_distance_meters=50 
    )

    if not nearby_hazards:
        return 0.0  # 위험요소 없으면 0.0점

    # 2. 위험도 가중치 계산
    point_risk = 0.0
    for hazard in nearby_hazards:
        type_weight = HAZARD_WEIGHTS.get(hazard.get("type"), 0.5)
        severity_weight = SEVERITY_WEIGHTS.get(hazard.get("severity"), 1.0)
        point_risk += (type_weight * severity_weight)
    
    # 3. exp 함수 적용
    # 0.0이면 math.exp(0) - 1 = 1 - 1 = 0.0 반환
    return math.exp(point_risk) - 1


async def compute_scores_for_path(path: List[Dict[str, float]]) -> Tuple[float, List[float]]:
    """
    [수정된 함수]
    경로(path) 상의 여러 지점을 기반으로 
    1. 경로 전체의 최종 안전 점수 (final_safety_score)
    2. 각 지점별 위험 점수 리스트 (point_risk_scores)
    를 계산하여 튜플로 반환합니다.
    """
    
    point_risk_scores = []
    total_risk_score = 0.0
    
    # 1. 경로(path)의 각 지점(point)을 순회하며 개별 위험 점수 계산
    for point in path:
        # 새로 만든 헬퍼 함수 호출
        point_risk = await compute_risk_for_point(point)
        point_risk_scores.append(point_risk)
        total_risk_score += point_risk # 개별 점수(exp(risk)-1)를 누적

    # 2. (최종 안전 점수 산출)
    final_safety_score = max(0, 100 - total_risk_score)

    # 튜플로 2개 값 반환
    return final_safety_score, point_risk_scores


async def attach_safety_info(route_candidates: List[Dict[str, Any]]) -> dict:
    """
    [수정된 함수]
    C단계의 route 후보들에 대해 hazard 기반 안전 점수 붙이기
    """
    safe_routes: List[SafeRouteOption] = []
    best_score = -1.0 # 안전 점수가 높을수록 좋다고 가정
    best_index = 0

    for i, route in enumerate(route_candidates):

        # [수정됨] 튜플로 2개의 값을 받음 (전체 점수, 개별 점수 리스트)
        score, segment_risks = await compute_scores_for_path(route["path"])

        segments = []
        # [수정됨] 개별 점수 리스트(segment_risks)를 사용
        # zip을 사용해 경로 지점(p)과 위험 점수(risk)를 1:1 매칭
        for p, risk in zip(route["path"], segment_risks):
            segments.append(
                SafeRouteSegment(
                    lat=p["lat"],
                    lon=p["lon"],
                    riskScore=risk  # <--- 0 대신 실제 계산된 risk 값
                )
            )

        safe_route = SafeRouteOption(
            distance=route["distance"],
            duration=route["duration"],
            safetyScore=score, # 경로 전체 점수
            path=segments      # 개별 점수가 포함된 경로
        )
        safe_routes.append(safe_route)

        if score > best_score:
            best_score = score
            best_index = i

    # [동일] 딕셔너리(dict)를 반환
    return {
        "routes": safe_routes,
        "bestRouteIndex": best_index
    }