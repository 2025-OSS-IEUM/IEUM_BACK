from fastapi import APIRouter, HTTPException, status
from datetime import datetime

from ..core.core import reports_collection
from ..utils.errors import err
from ..schemas.reports_schema import ReportCreate, ReportResponse

router = APIRouter(prefix="/reports", tags=["Reports"])

from fastapi import APIRouter, status
from datetime import datetime

from ..core.core import reports_collection
from ..utils.errors import err
from ..schemas.reports_schema import ReportCreate, ReportResponse

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post("/", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def create_report(report: ReportCreate):
    collection = reports_collection  # ← get_db() 대신 core에서 직접 가져옴

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
        if not inserted:
            return err("DB_READ_FAILED", "Inserted document could not be retrieved")

        # ObjectId → 문자열 변환
        inserted["id"] = str(inserted["_id"])
        del inserted["_id"]

        return inserted

    except Exception as e:
        return err("UNKNOWN_ERROR", "Unexpected server error", str(e))
