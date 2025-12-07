# api/services/safe_route_service.py

import asyncio
from typing import List, Dict, Any, Tuple

# 스키마 이름은 프로젝트에 맞게 확인해주세요
from schemas.safe_route_schema import (
    SafeRouteOption,
    SafeRouteSegment,
    SafeRouteResponse,
    SafeRouteRequest, # [NEW] 초기 요청 스키마 가정
    RerouteRequest
)
from db.database import find_hazards_near_coordinates
from core.config import HAZARD_WEIGHTS, SEVERITY_WEIGHTS
from services.tmap_directions import get_directions

# =========================================================
# [핵심] 3가지 경로 수집 공통 함수 (초기탐색 & 재탐색 모두 사용)
# =========================================================
async def fetch_and_process_diverse_routes(
    start_lat: float, start_lon: float, 
    end_lat: float, end_lon: float
) -> SafeRouteResponse:
    
    print(f"\n🚀 [경로 탐색 시작] {start_lat},{start_lon} -> {end_lat},{end_lon}")

    # 1. 3가지 옵션 정의 (추천 / 대로 / 최단)
    pedestrian_options = [0, 4, 10]
    
    # 2. 병렬 요청 (Log 찍기)
    print(f"📡 TMap에 3가지 옵션{pedestrian_options} 동시 요청 중...")
    
    tasks = [
        get_directions(start_lat, start_lon, end_lat, end_lon, search_option=opt)
        for opt in pedestrian_options
    ]
    
    results_list = await asyncio.gather(*tasks)
    
    # 3. 중복 제거 및 후보 통합
    all_candidates = []
    seen_paths = set()

    for i, result in enumerate(results_list):
        print(f"  ✅ Option {pedestrian_options[i]} 응답: {len(result)}개 경로 도착")
        for route in result:
            # 키: (거리, 시간) -> 이게 같으면 같은 경로로 간주
            route_key = (route.get('distance'), route.get('duration'))
            
            if route_key not in seen_paths:
                seen_paths.add(route_key)
                all_candidates.append(route)
            else:
                print(f"    🗑️ [중복] 거리 {route.get('distance')}m 경로는 이미 있어서 제외")

    print(f"🏁 최종 심사 대상 후보: {len(all_candidates)}개")

    # 4. 후보가 없으면 빈 값 반환
    if not all_candidates:
        print("🚨 [ERROR] 유효한 경로를 하나도 못 가져왔습니다.")
        return SafeRouteResponse(routes=[], bestRouteIndex=0)

    # 5. 안전 점수 계산 (기존 로직 연결)
    return await attach_safety_info(all_candidates)


# =========================================================
# 1. 초기 경로 탐색 함수 (앱에서 "길찾기" 누를 때 여기로 옴)
# =========================================================
async def calculate_safe_route(request: SafeRouteRequest) -> SafeRouteResponse:
    # 기존 코드는 get_directions를 1번만 불렀을 겁니다.
    # 이제 공통 함수를 써서 3개를 부르도록 변경합니다.
    return await fetch_and_process_diverse_routes(
        request.start_lat, request.start_lon,
        request.end_lat, request.end_lon
    )

# =========================================================
# 2. 재탐색 함수 (경로 이탈 시 여기로 옴)
# =========================================================
async def get_reroute_path(request: RerouteRequest) -> SafeRouteResponse:
    # 재탐색도 똑같이 공통 함수 사용!
    return await fetch_and_process_diverse_routes(
        request.current_lat, request.current_lon,
        request.dest_lat, request.dest_lon
    )


# ---------------------------------------
# (아래는 기존 계산 로직들 - 그대로 유지)
# ---------------------------------------

async def compute_risk_for_point(point: Dict[str, float]) -> float:
    try:
        lon = float(point["lon"])
        lat = float(point["lat"])
    except (ValueError, TypeError):
        return 0.0

    nearby_hazards = await find_hazards_near_coordinates(
        coordinates=[lon, lat], max_distance_meters=50
    )

    if not nearby_hazards:
        return 0.0

    total_weight = 0.0
    for hazard in nearby_hazards:
        type_w = HAZARD_WEIGHTS.get(hazard.get("type"), 0.5)
        severity_w = SEVERITY_WEIGHTS.get(hazard.get("severity"), 1.0)
        total_weight += type_w * severity_w

    return min(total_weight * 5.0, 50.0)

async def compute_scores_for_path(path: List[Dict[str, float]]) -> Tuple[float, List[float]]:
    if not path:
        return 0.0, []

    tasks = [compute_risk_for_point(point) for point in path]
    point_risk_scores = await asyncio.gather(*tasks)
    
    total_risk_sum = sum(point_risk_scores)
    path_length = len(point_risk_scores)
    avg_risk = total_risk_sum / path_length if path_length > 0 else 0
    
    penalty_score = avg_risk * 1.5 + (total_risk_sum * 0.05)
    final_safety_score = max(0, 100 - penalty_score)

    return float(final_safety_score), list(point_risk_scores)

async def attach_safety_info(route_candidates: List[Dict[str, Any]]) -> SafeRouteResponse:
    safe_routes: List[SafeRouteOption] = []
    best_score = -1.0
    best_index = 0

    for idx, route in enumerate(route_candidates):
        path_data = route.get("path", [])
        if not path_data:
            continue

        score, segment_risks = await compute_scores_for_path(path_data)
        
        # [로그 확인] 여기서 점수가 찍혀야 합니다!
        print(f"👉 후보 {idx}번 (옵션섞임) | 안전점수: {score:.2f}점 | 거리: {route.get('distance')}m")

        segments = [
            SafeRouteSegment(lat=p["lat"], lon=p["lon"], riskScore=r)
            for p, r in zip(path_data, segment_risks)
        ]

        safe_routes.append(SafeRouteOption(
            distance=route["distance"],
            duration=route["duration"],
            safetyScore=score,
            path=segments
        ))

        if score > best_score:
            best_score = score
            best_index = idx
        elif score == best_score:
            if route["distance"] < route_candidates[best_index]["distance"]:
                best_index = idx

    print(f"👑 최종 선정된 베스트 경로 인덱스: {best_index}")

    return SafeRouteResponse(
        routes=safe_routes,
        bestRouteIndex=best_index
    )