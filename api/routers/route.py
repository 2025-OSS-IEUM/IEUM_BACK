from fastapi import APIRouter, status
from schemas.route_schema import (
    RouteRequest,
    RouteResponse,
    RouteOption,
    RoutePoint,
)
from services.kakao_directions import fetch_kakao_routes
from core.errors import ErrorCodes, raise_error

router = APIRouter(prefix="/route", tags=["Route"])


# ===============================
# 📌 (C) POST /route
# ===============================
@router.post("/", response_model=RouteResponse, status_code=status.HTTP_200_OK)
async def get_route_candidates(req: RouteRequest):
    """(C) Kakao Directions 기반 경로 후보 조회"""

    # 1) Kakao API 호출
    try:
        raw = await fetch_kakao_routes(
            req.start_lat,
            req.start_lon,
            req.end_lat,
            req.end_lon,
        )
    except Exception:
        raise_error(ErrorCodes.SERVER_ERROR)

    # 2) Kakao API 결과 파싱
    routes = []

    try:
        for option in raw.get("routes", []):
            summary = option["summary"]
            distance = summary["distance"]
            duration = summary["duration"]

            path = []
            for section in option["sections"]:
                for road in section["roads"]:
                    v = road["vertexes"]
                    # vertexes = [lon, lat, lon, lat ...]
                    for i in range(0, len(v), 2):
                        lon = v[i]
                        lat = v[i + 1]
                        path.append(RoutePoint(lat=lat, lon=lon))

            routes.append(RouteOption(
                distance=distance,
                duration=duration,
                path=path
            ))

    except Exception:
        raise_error(ErrorCodes.SERVER_ERROR)

    return RouteResponse(routes=routes)
