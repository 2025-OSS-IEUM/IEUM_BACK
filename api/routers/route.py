from fastapi import APIRouter, status
from schemas.route_schema import (
    RouteRequest,
    RouteResponse,
    RouteOption,
    RoutePoint,
)
from services.tmap_directions import get_directions
from core.errors import ErrorCodes, raise_error

router = APIRouter(prefix="/route", tags=["Route"])


# ===============================
# 📌 (C) POST /route
# ===============================
@router.post("/", response_model=RouteResponse, status_code=status.HTTP_200_OK)
async def get_route_candidates(req: RouteRequest):
    """(C) Tmap Directions 기반 도보 경로 후보 조회"""

    # 1) Tmap API 호출 및 파싱 (서비스 함수 위임)
    try:
        # get_directions 함수가 이미 Tmap 데이터를 받아서 
        # [{'distance':..., 'duration':..., 'path': [{'lat':.., 'lon':..}]}] 형태로 줍니다.
        parsed_routes = await get_directions(
            req.start_lat,
            req.start_lon,
            req.end_lat,
            req.end_lon,
        )
    except Exception as e:
        print(f"[Router Error] {e}")
        raise_error(ErrorCodes.SERVER_ERROR)

    # 2) Pydantic 모델로 변환 (Dict -> Schema)
    routes = []
    
    # get_directions가 빈 리스트를 반환할 수도 있음
    if not parsed_routes:
        # 경로가 없으면 빈 리스트 반환하거나 에러 처리 (여기선 빈 리스트)
        return RouteResponse(routes=[])

    for r_dict in parsed_routes:
        # 'path' 내부의 dict 리스트를 RoutePoint 객체 리스트로 변환
        path_objs = [
            RoutePoint(lat=p["lat"], lon=p["lon"]) 
            for p in r_dict["path"]
        ]

        routes.append(RouteOption(
            distance=r_dict["distance"],
            duration=r_dict["duration"],
            path=path_objs
        ))

    return RouteResponse(routes=routes)