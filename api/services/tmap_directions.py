import httpx
from typing import List, Dict, Any

from core.config import settings
from core.errors import ErrorCodes, raise_error

# ----------------------------------------------------
# 1. Tmap 보행자 API 원본 데이터를 가져오는 함수 (Kakao 대체)
# ----------------------------------------------------
async def fetch_tmap_routes(start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> Dict[str, Any]:
    """
    Tmap 보행자 경로 안내 API를 호출하여 원본 JSON 데이터를 반환합니다.
    학교 내부 샛길, 인도, 계단 등을 포함한 경로를 제공합니다.
    """
    url = "https://apis.openapi.sk.com/tmap/routes/pedestrian?version=1"

    headers = {
        "appKey": settings.TMAP_API_KEY,  # .env 또는 config에 정의된 키 사용
        "Content-Type": "application/json"
    }

    # Tmap 요청 파라미터 (좌표계는 WGS84GEO = 위경도 사용)
    payload = {
        "startX": start_lon,
        "startY": start_lat,
        "endX": end_lon,
        "endY": end_lat,
        "reqCoordType": "WGS84GEO", 
        "resCoordType": "WGS84GEO",
        "startName": "Start", # 필수값이지만 로직엔 영향 없음
        "endName": "End",
        "searchOption": "0"   # 0: 추천 경로 (가장 무난함)
    }

    try:
        async with httpx.AsyncClient() as client:
            # Tmap은 POST 방식을 권장합니다.
            res = await client.post(url, headers=headers, json=payload)
            res.raise_for_status()
            
            raw_data = res.json()
            
            # Tmap 결과 검증
            if "features" not in raw_data:
                 raise ValueError("Tmap API에서 경로를 찾지 못했습니다.")

            return raw_data

    except Exception as e:
        print(f"[Tmap Error] {e}")
        # 에러 발생 시 서버 에러로 처리
        raise_error(ErrorCodes.SERVER_ERROR)

# ----------------------------------------------------
# 2. 안전 경로 서비스에서 사용할 형태로 변환하는 함수
# ----------------------------------------------------
async def get_directions(start_lat: float, start_lon: float, end_lat: float, end_lon: float) -> List[Dict[str, Any]]:
    """
    Tmap의 GeoJSON 데이터를 파싱하여 SafeRouteService가 처리할 수 있는
    경로 후보 목록 (List[Dict]) 형태로 반환합니다.
    """
    try:
        raw_data = await fetch_tmap_routes(start_lat, start_lon, end_lat, end_lon)
    except Exception:
        return []

    path_points = []
    total_distance = 0
    total_time = 0

    # Tmap 보행자 경로는 GeoJSON 포맷인 'features' 리스트로 쪼개져서 옵니다.
    features = raw_data.get('features', [])

    for feature in features:
        geometry = feature['geometry']
        properties = feature['properties']

        # 1) 전체 경로 요약 정보 (보통 첫 번째 Point feature에 들어있음)
        if 'totalDistance' in properties:
            total_distance = properties['totalDistance'] # 단위: m
            total_time = properties['totalTime']         # 단위: 초

        # 2) 경로 좌표 추출
        # Tmap은 'Point'(지점)와 'LineString'(경로선)이 섞여 옵니다.
        # 지도에 선을 그리기 위해서는 'LineString'의 좌표들만 가져오면 됩니다.
        if geometry['type'] == 'LineString':
            coords = geometry['coordinates']
            
            # Tmap 좌표는 [lon, lat] 순서이므로, 우리 포맷인 {lat, lon}으로 변환
            for lon, lat in coords:
                path_points.append({"lat": lat, "lon": lon})
        
        # (참고) Point 타입은 '우회전', '육교 진입' 같은 안내 지점 정보입니다.
        # 필요하다면 여기서 properties['description'] 등을 활용할 수 있습니다.

    # 기존 로직과 호환되도록 리스트로 감싸서 반환
    return [{
        "distance": total_distance,
        "duration": total_time,
        "path": path_points
    }]