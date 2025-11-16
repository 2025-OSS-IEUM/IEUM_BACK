# api/routers/safe_route.py

from fastapi import APIRouter
# TODO: 나중에 attach_safety_info import 예정
# from services.safe_route_service import attach_safety_info

router = APIRouter(
    prefix="/routes",
    tags=["Routes"]
)

@router.get("/safe/debug")
async def safe_route_debug():
    """
    D단계 뼈대 라우터.
    TODO:
    - E단계에서 POST /routes/safe 로 변경
    - 실제 안전 경로 서비스와 연결
    """
    return {
        "message": "safe_route_service connected (D 단계 뼈대)"
    }
