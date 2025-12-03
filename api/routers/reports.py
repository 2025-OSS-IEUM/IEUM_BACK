from fastapi import APIRouter, status, Query, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime
from typing import List, Optional

from db.database import reports_collection, users_collection
from schemas.report_schema import (
    ReportCreate,
    ReportResponse,
    HazardType,
    Status,
)
from core.errors import ErrorCodes, raise_error
from core.security import verify_token

router = APIRouter(prefix="/reports", tags=["Reports"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ===============================
# 📌 (B-2) POST /reports — 제보 생성
# ===============================
@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(
    report: ReportCreate,
    token: str = Depends(oauth2_scheme)
):
    sub = verify_token(token)
    if sub is None:
        raise_error(ErrorCodes.INVALID_CREDENTIALS)

    # username → user_id
    user = await users_collection.find_one({"username": sub}, {"user_id": 1, "_id": 0})
    if not user:
        raise_error(ErrorCodes.USERNAME_NOT_FOUND)
    current_user_id = user["user_id"]

    # 중복 제보 체크
    existing = await reports_collection.find_one({
        "location.coordinates": report.location.coordinates,
        "type": report.type,
        "status": {"$ne": "resolved"}
    })
    if existing:
        raise_error(ErrorCodes.REPORT_ALREADY_EXISTS)

    # 저장 문서 구성
    new_doc = report.model_dump()

    # 🔥 severity는 숫자로 그대로 저장
    # (문자열 변환 없음)
    new_doc["severity"] = report.severity

    new_doc["user_id"] = current_user_id
    new_doc["createdAt"] = datetime.utcnow()
    new_doc["status"] = "pending_review"

    result = await reports_collection.insert_one(new_doc)
    if not result.inserted_id:
        raise_error(ErrorCodes.SERVER_ERROR)

    inserted = await reports_collection.find_one({"_id": result.inserted_id})
    if not inserted:
        raise_error(ErrorCodes.SERVER_ERROR)

    inserted["id"] = str(inserted["_id"])
    return inserted


# ===============================
# 📌 (B-3) GET /reports — 제보 조회
# ===============================
@router.get("/", response_model=List[ReportResponse], status_code=status.HTTP_200_OK)
async def get_reports_by_bbox_and_filters(
    min_lon: float = Query(..., ge=-180, le=180),
    min_lat: float = Query(..., ge=-90, le=90),
    max_lon: float = Query(..., ge=-180, le=180),
    max_lat: float = Query(..., ge=-90, le=90),

    type: Optional[HazardType] = Query(None),
    severity: Optional[int] = Query(None, ge=1, le=5),  # 🔥 문자열 → 숫자로 변경
    status: Optional[Status] = Query(None),

    limit: int = Query(100, ge=1, le=1000),
):
    filter_query = {}

    if type:
        filter_query["type"] = type
    if severity is not None:
        filter_query["severity"] = severity  # 🔥 숫자로 필터
    if status:
        filter_query["status"] = status

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
