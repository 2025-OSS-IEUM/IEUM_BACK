from typing import List, Dict, Tuple
from math import radians, sin, cos, sqrt, atan2

def haversine_m(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    두 위경도 좌표 간 거리를 미터 단위로 계산하는 함수 (Haversine 공식)
    p1, p2: (lng, lat) 형태의 튜플
    """
    R = 6371000  # 지구 반지름 (m)
    lon1, lat1 = p1
    lon2, lat2 = p2

    dlon = radians(lon2 - lon1)
    dlat = radians(lat2 - lat1)

    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c  # 두 지점 간 거리(m)

def calculate_risk(route: List[Tuple[float, float]], hazards: List[Dict], threshold_m: float = 8.0) -> int:
    """
    경로(route)의 각 점과 hazard 지점 간 거리를 계산하여 위험 점수 반환
    - threshold_m 미터 이내의 hazard가 있으면 위험 1점
    - 경로에 하나라도 가까우면 그 hazard는 1회만 카운트 (중복 방지)
    """
    danger_hits = 0

    for h in hazards:
        hpt = (h["lng"], h["lat"])  # hazard 좌표
        for lng, lat in route:
            if haversine_m((lng, lat), hpt) <= threshold_m:
                danger_hits += 1
                break  # 해당 hazard는 한 번만 카운트

    return danger_hits

def choose_safest_route(routes: List[List[Tuple[float, float]]], hazards: List[Dict]) -> Dict:
    """
    여러 후보 경로 중 위험 점수가 가장 낮은 경로 선택
    - 각 경로마다 calculate_risk 수행
    - risk가 가장 낮은 경로를 best로 반환
    """
    scored = []

    for i, r in enumerate(routes):
        score = calculate_risk(r, hazards)
        scored.append({
            "route_index": i,
            "risk": score,
            "coords": r,
        })

    # 위험 점수가 가장 낮은 경로 선택
    safest = min(scored, key=lambda x: x["risk"])

    return {
        "all_scores": scored,  # 모든 경로의 위험 점수 리스트
        "best": safest         # 최종 선택된 경로 정보
    }

# 단독 실행 테스트
if __name__ == "__main__":
    routes = [
        [(127.0, 37.0), (127.001, 37.001)],  # 경로 A
        [(127.0, 37.0), (127.002, 37.002)],  # 경로 B
        [(127.0, 37.0), (127.003, 37.003)]   # 경로 C
    ]

    hazards = [{"lng":127.001, "lat":37.001}]

    result = choose_safest_route(routes, hazards)
    print(result)
