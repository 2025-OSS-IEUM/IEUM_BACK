from fastapi import APIRouter, status, Query  # Query 추가
from datetime import datetime
from typing import List, Optional  # List, Optional 추가

from app.db.mongo import get_db
from app.utils.errors import err

# (중요) 스키마 파일에서 모델 및 타입들을 가져옵니다.
from api.schemas.reports_schema import (
    ReportCreate,
    ReportResponse,
    HazardType,
    Severity,
    Status,
)
# 만약 위 import가 오류나면, 이전에 보여주신 파일 경로를 사용하세요:
# from app.models.hazard_report import HazardType, Severity, Status


router = APIRouter(prefix="/reports", tags=["Reports"])


# ===============================
# 📌 (B-2) POST /reports 
# ===============================
@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(report: ReportCreate):
    db = get_db()
    collection = db["hazard_reports"]

    try:
        # 좌표 유효성 검사
        if len(report.location.coordinates) != 2:
            return err("VALIDATION_ERROR", "Invalid coordinates: must contain [lng, lat]")

        # 중복 제보 확인 (같은 좌표 + 타입)
        existing = await collection.find_one({
            "location.coordinates": report.location.coordinates,
            "type": report.type
        })
        if existing:
            return err("DUPLICATE_REPORT", "Report already exists for this location and type")

        # MongoDB에 데이터 삽입
        new_doc = report.dict()
        new_doc["createdAt"] = datetime.utcnow()

        result = await collection.insert_one(new_doc)
        if not result.inserted_id:
            return err("DB_INSERT_FAILED", "Failed to insert report into database")

        # 삽입된 문서 조회
        inserted = await collection.find_one({"_id": result.inserted_id})
        inserted["id"] = str(inserted["_id"])  # _id -> id 변환
        del inserted["_id"]

        return inserted

    except Exception as e:
        return err("UNKNOWN_ERROR", "Unexpected server error", str(e))


# ==================================
# 📌 (B-3) GET /reports 
# ==================================
@router.get("/", response_model=List[ReportResponse], status_code=status.HTTP_200_OK)
async def get_reports_by_bbox_and_filters(
    # 1. Bbox 쿼리 파라미터 (필수)
    min_lon: float = Query(..., description="최소 경도 (Longitude)", ge=-180, le=180),
    min_lat: float = Query(..., description="최소 위도 (Latitude)", ge=-90, le=90),
    max_lon: float = Query(..., description="최대 경도 (Longitude)", ge=-180, le=180),
    max_lat: float = Query(..., description="최대 위도 (Latitude)", ge=-90, le=90),

    # 2. 필터링 쿼리 파라미터 (선택)
    type: Optional[HazardType] = Query(None, description="제보 유형 필터"),
    severity: Optional[Severity] = Query(None, description="심각도 필터"),
    status: Optional[Status] = Query(None, description="상태 필터"),

    # 3. 페이징
    limit: int = Query(100, description="최대 반환 개수", ge=1, le=1000)
):
    """
    Bbox 및 필터 기준으로 위험/불편사항 제보(Report) 조회
    - 2dsphere 인덱스를 활용한 $geoWithin 쿼리 사용
    """
    db = get_db()
    collection = db["hazard_reports"]

    try:
        # 1. 기본 필터 쿼리 구성 (type, severity, status)
        filter_query = {}
        if type:
            filter_query["type"] = type
        if severity:
            filter_query["severity"] = severity
        if status:
            filter_query["status"] = status

        # 2. Bbox 기반 MongoDB 공간 쿼리 ($geoWithin, $box) 추가
        # $box는 [ [bottom_left_lon, bottom_left_lat], [top_right_lon, top_right_lat] ]
        filter_query["location"] = {
            "$geoWithin": {
                "$box": [
                    [min_lon, min_lat],  # Bottom-left corner
                    [max_lon, max_lat]   # Top-right corner
                ]
            }
        }

        # 3. MongoDB에서 쿼리 실행 (2dsphere 인덱스 활용)
        cursor = collection.find(filter_query).limit(limit)
        reports = await cursor.to_list(length=limit)

        # 4. _id -> id 변환 (POST와 동일한 응답 스키마를 맞추기 위해)
        processed_reports = []
        for report in reports:
            report["id"] = str(report["_id"])
            del report["_id"]
            processed_reports.append(report)
        
        return processed_reports

    except Exception as e:
        return err("UNKNOWN_ERROR", "Failed to retrieve reports", str(e))