# api/routers/safe_route.py

from fastapi import APIRouter, Body
from typing import List, Dict, Any

# 🔽 (1) 주석을 해제하고 실제 서비스 함수를 임포트합니다.
from services.safe_route_service import attach_safety_info

# 🔽 (2) 응답에 사용할 스키마를 임포트합니다.
from schemas.safe_route_schema import SafeRouteResponse 

router = APIRouter(
    prefix="/routes",
    tags=["Routes"]
)

# 🔽 (3) 기존 GET /safe/debug 뼈대 라우터를
# E단계 계획(image_ad5810.jpg)에 맞게 POST /safe로 변경합니다.

@router.post("/safe", response_model=SafeRouteResponse)
async def get_safe_route_with_scores(
    # 🔽 (4) "하드코딩 하지 말고" -> C단계의 경로 후보 리스트를 Request Body로 받습니다.
    route_candidates: List[Dict[str, Any]] = Body(
        ...,
        example=[ # Swagger UI에 보일 예시 데이터
            {
                "distance": 1500,
                "duration": 900,
                "path": [
                    {"lat": 37.501, "lon": 127.041},
                    {"lat": 37.502, "lon": 127.042}
                ]
            },
            {
                "distance": 1600,
                "duration": 950,
                "path": [
                    {"lat": 37.601, "lon": 127.051},
                    {"lat": 37.605, "lon": 127.055}
                ]
            }
        ]
    )
):
    """
    (D/E단계) C단계에서 수집한 경로 후보 리스트(Body)를 받아,
    위험 요소를 쿼리하고 점수를 계산한 뒤,
    안전 정보가 포함된 경로 옵션들을 반환합니다.
    """
    
    # 🔽 (5) Body로 받은 데이터를 실제 서비스 로직으로 전달
    safe_route_response = await attach_safety_info(route_candidates)
    
    return safe_route_response