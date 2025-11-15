from fastapi import APIRouter, status, Query, HTTPException, Body
from datetime import datetime
from typing import List, Optional
from bson import ObjectId

# 1. (FIXED) 'api/db/database.py'에서 컬렉션을 직접 가져옵니다.
from db.database import reports_collection

# 2. (FIXED) 'api/schemas/report_schema.py'에서 스키마를 가져옵니다.
from schemas.report_schema import (
    ReportCreate,
    ReportResponse,
    HazardType,
    Severity,
    Status,
)

router = APIRouter(prefix="/reports", tags=["Reports"])


# ===============================
# 📌 (B-2) POST /reports 
# (Schema validator handles coordinate checks)
# ===============================
@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(report: ReportCreate):
    """(B-2) 위험/불편사항 제보(Report) 생성"""
    
    # (FIXED) Use the imported 'reports_collection' directly
    try:
        # --- (CLEANUP) ---
        # `if len(report.location.coordinates) != 2:`
        # 위 좌표 검사 로직이 제거되었습니다.
        # 'api/schemas/report_schema.py'의 GeoJSONPoint 모델에 있는
        # '@field_validator'가 이 검사를 자동으로 수행합니다.
        # ---------------------

        # 중복 제보 확인 (같은 좌표 + 타입)
        existing = await reports_collection.find_one({
            "location.coordinates": report.location.coordinates,
            "type": report.type
        })
        if existing:
            # (FIXED) Use HTTPException for duplicate errors
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, 
                detail="Report already exists for this location and type"
            )

        # MongoDB에 데이터 삽입
        # (FIXED) Use Pydantic v2's .model_dump()
        new_doc = report.model_dump()
        new_doc["createdAt"] = datetime.utcnow()

        result = await reports_collection.insert_one(new_doc)
        if not result.inserted_id:
            # (FIXED) Use HTTPException for DB errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Failed to insert report into database"
            )

        # 삽입된 문서 조회
        inserted = await reports_collection.find_one({"_id": result.inserted_id})
        
        if not inserted:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail="Failed to retrieve newly created report"
            )
            
        # _id -> id 변환 (ReportResponse 스키마에 맞게)
        inserted["id"] = str(inserted["_id"])
        
        return inserted
    except HTTPException as http_exc:
        # 1. HTTPException (예: 409)을 먼저 잡아서 그대로 반환합니다.
        raise http_exc

    except Exception as e:
        # (FIXED) Use HTTPException for unknown errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Unexpected server error: {e}"
        )


# ==================================
# 📌 (B-3) GET /reports 
# (Bbox query uses the 2dsphere index)
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
    """(B-3) Bbox 및 필터 기준으로 위험/불편사항 제보(Report) 조회"""
    
    # (FIXED) Use the imported 'reports_collection' directly
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
        filter_query["location"] = {
            "$geoWithin": {
                "$box": [
                    [min_lon, min_lat],  # Bottom-left corner
                    [max_lon, max_lat]   # Top-right corner
                ]
            }
        }

        # 3. MongoDB에서 쿼리 실행 (2dsphere 인덱스 활용)
        cursor = reports_collection.find(filter_query).limit(limit)
        reports = await cursor.to_list(length=limit)

        # 4. _id -> id 변환 (POST와 동일한 응답 스키마를 맞추기 위해)
        processed_reports = []
        for report in reports:
            report["id"] = str(report["_id"])
            processed_reports.append(report)
        
        return processed_reports

    except Exception as e:
        # (FIXED) Use HTTPException
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to retrieve reports: {e}"
        )