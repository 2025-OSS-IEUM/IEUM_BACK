from fastapi import APIRouter, status, Query
from datetime import datetime
from typing import List, Optional

from db.database import reports_collection
from schemas.report_schema import (  # "safe_route_schema" -> 다시 "report_schema"로!
    ReportCreate,
    ReportResponse,
    HazardType,
    Severity,
    Status,
)

# errors.py
from core.errors import ErrorCodes, raise_error

router = APIRouter(prefix="/reports", tags=["Reports"])


# ===============================
# 📌 (B-2) POST /reports
# ===============================
@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(report: ReportCreate):
    """(B-2) 위험/불편사항 제보 생성"""

    # 1) 동일 위치 + 동일 타입 제보 체크
    existing = await reports_collection.find_one({
        "location.coordinates": report.location.coordinates,
        "type": report.type
    })
    if existing:
        raise_error(ErrorCodes.REPORT_ALREADY_EXISTS)

    # 2) 저장 데이터 구성
    new_doc = report.model_dump()
    new_doc["createdAt"] = datetime.utcnow()

    # 3) DB 저장
    result = await reports_collection.insert_one(new_doc)
    if not result.inserted_id:
        raise_error(ErrorCodes.SERVER_ERROR)

    # 4) 저장된 문서 다시 조회
    inserted = await reports_collection.find_one({"_id": result.inserted_id})
    if not inserted:
        raise_error(ErrorCodes.SERVER_ERROR)

    # 5) 응답 스키마에 맞도록 id 변환
    inserted["id"] = str(inserted["_id"])
    return inserted


# ===============================
# 📌 (B-3) GET /reports
# ===============================
@router.get("/", response_model=List[ReportResponse], status_code=status.HTTP_200_OK)
async def get_reports_by_bbox_and_filters(
    # -------------------------------------
    # 1. 필수 BBox 범위 설정
    # -------------------------------------
    min_lon: float = Query(
        ..., 
        description="최소 경도(Longitude). 지도 좌하단 모서리의 경도값입니다.",
        ge=-180, le=180,
    ),
    min_lat: float = Query(
        ...,
        description="최소 위도(Latitude). 지도 좌하단 모서리의 위도값입니다.",
        ge=-90, le=90,
    ),
    max_lon: float = Query(
        ...,
        description="최대 경도(Longitude). 지도 우상단 모서리의 경도값입니다.",
        ge=-180, le=180,
    ),
    max_lat: float = Query(
        ...,
        description="최대 위도(Latitude). 지도 우상단 모서리의 위도값입니다.",
        ge=-90, le=90,
    ),

    # -------------------------------------
    # 2. 옵션 필터
    # -------------------------------------
    type: Optional[HazardType] = Query(
        None,
        description="제보 유형 필터. 특정 위험 유형만 조회할 때 사용합니다."
    ),
    severity: Optional[Severity] = Query(
        None,
        description="심각도(severity) 필터. low / medium / high 중 선택."
    ),
    status: Optional[Status] = Query(
        None,
        description="제보 상태(status) 필터. 예: pending_review / approved / resolved."
    ),

    # -------------------------------------
    # 3. 페이징
    # -------------------------------------
    limit: int = Query(
        100,
        description="최대 조회 개수. 기본 100개이며 1~1000 범위로 설정할 수 있습니다.",
        ge=1, le=1000,
    ),
):
    """(B-3) BBox + 필터 기반 제보 조회"""

    # 1) 기본 필터 설정
    filter_query = {}
    if type:
        filter_query["type"] = type
    if severity:
        filter_query["severity"] = severity
    if status:
        filter_query["status"] = status

    # 2) BBox 공간 쿼리 추가
    filter_query["location"] = {
        "$geoWithin": {
            "$box": [
                [min_lon, min_lat],  # 좌하단
                [max_lon, max_lat],  # 우상단
            ]
        }
    }

    # 3) DB 조회
    try:
        cursor = reports_collection.find(filter_query).limit(limit)
        reports = await cursor.to_list(length=limit)
    except Exception:
        raise_error(ErrorCodes.SERVER_ERROR)

    # 4) _id → id 변환
    for r in reports:
        r["id"] = str(r["_id"])

    return reports
