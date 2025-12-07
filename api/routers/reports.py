from fastapi import APIRouter, status, Query, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime
from typing import List, Optional

# DB 관련
from db.database import reports_collection, users_collection

# 스키마 관련
from schemas.report_schema import (
    ReportCreate,
    ReportResponse,
    HazardType,
    Severity,
    Status,
)

# 보안 및 에러 관련
from core.errors import ErrorCodes, raise_error
from core.security import verify_token

router = APIRouter(prefix="/reports", tags=["Reports"])

# 토큰 인증을 위한 스키마 (로그인 URL은 프로젝트 설정에 맞게)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ===============================
# 📌 (B-2) POST /reports — 제보 생성 
# ===============================
@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(report: ReportCreate):

    existing = await reports_collection.find_one({
        "location.coordinates": report.location.coordinates,
        "type": report.type
    })
    if existing:
        raise_error(ErrorCodes.REPORT_ALREADY_EXISTS)

    new_doc = report.model_dump()
    new_doc["createdAt"] = datetime.utcnow()

    result = await reports_collection.insert_one(new_doc)
    inserted = await reports_collection.find_one({"_id": result.inserted_id})

    inserted["id"] = str(inserted["_id"])
    return inserted


    # ---------------------------------------
    # 2. 중복 제보 체크
    # ---------------------------------------
    existing = await reports_collection.find_one({
        "location.coordinates": report.location.coordinates,
        "type": report.type,
        "status": {"$ne": "RESOLVED"} # (선택사항) 해결된 건은 중복이어도 될 수 있으니 체크 로직 보완 가능
    })
    
    # 같은 위치, 같은 타입인데 아직 해결되지 않은 제보가 있다면 중복 처리
    if existing:
        raise_error(ErrorCodes.REPORT_ALREADY_EXISTS)

    # ---------------------------------------
    # 3. 데이터 저장 준비
    # ---------------------------------------
    new_doc = report.model_dump()
    new_doc["user_id"] = current_user_id  # 👈 작성자 ID 주입
    new_doc["createdAt"] = datetime.utcnow()
    new_doc["status"] = Status.REPORTED     # 초기 상태 강제 지정 (스키마 기본값이 있다면 생략 가능)

    # ---------------------------------------
    # 4. DB 저장
    # ---------------------------------------
    result = await reports_collection.insert_one(new_doc)
    if not result.inserted_id:
        raise_error(ErrorCodes.SERVER_ERROR)

    # ---------------------------------------
    # 5. 저장된 문서 반환
    # ---------------------------------------
    inserted = await reports_collection.find_one({"_id": result.inserted_id})
    if not inserted:
        raise_error(ErrorCodes.SERVER_ERROR)

    inserted["id"] = str(inserted["_id"])
    return inserted


# ===============================
# 📌 (B-3) GET /reports — 제보 조회 (공개)
# ===============================
@router.get("/", response_model=List[ReportResponse], status_code=status.HTTP_200_OK)
async def get_reports_by_bbox_and_filters(
    min_lon: float = Query(..., ge=-180, le=180),
    min_lat: float = Query(..., ge=-90, le=90),
    max_lon: float = Query(..., ge=-180, le=180),
    max_lat: float = Query(..., ge=-90, le=90),

    type: Optional[HazardType] = Query(None),
    severity: Optional[Severity] = Query(None),
    status: Optional[Status] = Query(None),

    limit: int = Query(100, ge=1, le=1000),
):
    """(B-3) BBox + 필터 기반 제보 조회 (로그인 없이 조회 가능)"""

    filter_query = {}

    if type:
        filter_query["type"] = type
    if severity:
        filter_query["severity"] = severity
    if status:
        filter_query["status"] = status

    # GeoJSON 쿼리
    filter_query["location"] = {
        "$geoWithin": {
            "$box": [
                [min_lon, min_lat],
                [max_lon, max_lat],
            ]
        }
    }

    try:
        cursor = reports_collection.find(filter_query).limit(limit)
        reports = await cursor.to_list(length=limit)
    except Exception:
        raise_error(ErrorCodes.SERVER_ERROR)

    for r in reports:
        r["id"] = str(r["_id"])

    return reports