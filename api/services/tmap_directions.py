import httpx
from typing import List, Dict, Any
from core.config import settings
from core.errors import ErrorCodes, raise_error

# ----------------------------------------------------
# 1. Tmap 보행자 API 원본 데이터를 가져오는 함수
# ----------------------------------------------------
async def fetch_tmap_routes(
    start_lat: float, 
    start_lon: float, 
    end_lat: float, 
    end_lon: float,
    search_option: int = 0  # <--- [변경] 옵션 인자 추가 (기본값 0)
) -> Dict[str, Any]:
    """
    Tmap 보행자 경로 안내 API를 호출하여 원본 JSON 데이터를 반환합니다.
    search_option: 0(추천), 4(대로우선), 10(최단거리) 등
    """
    url = "https://apis.openapi.sk.com/tmap/routes/pedestrian?version=1"

    headers = {
        "appKey": settings.TMAP_API_KEY, 
        "Content-Type": "application/json"
    }

    # Tmap 요청 파라미터
    payload = {
        "startX": start_lon,
        "startY": start_lat,
        "endX": end_lon,
        "endY": end_lat,
        "reqCoordType": "WGS84GEO", 
        "resCoordType": "WGS84GEO",
        "startName": "Start", 
        "endName": "End",
        "searchOption": str(search_option)   # <--- [변경] 입력받은 옵션을 적용
    }

    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(url, headers=headers, json=payload)
            res.raise_for_status()
            
            raw_data = res.json()
            
            if "features" not in raw_data:
                 raise ValueError("Tmap API에서 경로를 찾지 못했습니다.")

            return raw_data

    except Exception as e:
        print(f"[Tmap Error] {e}")
        # 필요하다면 여기서 에러를 raise 하지 않고 빈 dict를 리턴하여 
        # 다른 옵션의 경로는 정상적으로 받도록 처리할 수도 있음
        raise_error(ErrorCodes.SERVER_ERROR)

# ----------------------------------------------------
# 2. 안전 경로 서비스에서 사용할 형태로 변환하는 함수
# ----------------------------------------------------
async def get_directions(
    start_lat: float, 
    start_lon: float, 
    end_lat: float, 
    end_lon: float,
    search_option: int = 0  # <--- [변경] 옵션 인자 추가 및 전달
) -> List[Dict[str, Any]]:
    """
    Tmap의 GeoJSON 데이터를 파싱하여 SafeRouteService가 처리할 수 있는
    경로 후보 목록 (List[Dict]) 형태로 반환합니다.
    """
    try:
        # [변경] search_option을 전달합니다.
        raw_data = await fetch_tmap_routes(start_lat, start_lon, end_lat, end_lon, search_option)
    except Exception:
        # API 호출 실패 시 빈 리스트 반환 (다른 옵션의 경로라도 살리기 위해)
        return []

    path_points = []
    total_distance = 0
    total_time = 0

    features = raw_data.get('features', [])

    for feature in features:
        geometry = feature['geometry']
        properties = feature['properties']

        # 1) 전체 경로 요약 정보 (보통 첫 번째 Feature에 전체 정보가 있음)
        if 'totalDistance' in properties:
            total_distance = properties['totalDistance'] 
            total_time = properties['totalTime']       

        # 2) 경로 좌표 추출 (LineString만 추출)
        if geometry['type'] == 'LineString':
            coords = geometry['coordinates']
            
            for lon, lat in coords:
                path_points.append({"lat": lat, "lon": lon})
        
    # 하나의 경로 옵션에 대한 결과이므로 리스트에 담아 반환
    return [{
        "distance": total_distance,
        "duration": total_time,
        "path": path_points
    }]