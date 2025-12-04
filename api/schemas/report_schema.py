from pydantic import BaseModel, Field, ConfigDict, BeforeValidator
from typing import List, Optional, Literal, Annotated
from datetime import datetime

# ObjectId를 문자열로 자동 변환하기 위한 유틸리티 타입
PyObjectId = Annotated[str, BeforeValidator(str)]

# --- 공통 Enum 정의 ---
HazardType = Literal[
    "sidewalk_damage", "construction", "missing_crosswalk", "no_tactile", "etc"
]
Severity = Literal["low", "medium", "high"]
Status = Literal["pending_review", "approved", "resolved"]

# --- GeoJSON 포맷 ---
class GeoJSONPoint(BaseModel):
    type: Literal["Point"] = "Point"
    coordinates: List[float] = Field(
        ...,
        min_length=2,
        max_length=2,
        description="[lng, lat] in decimal degrees",
        example=[127.043, 37.501]
    )

# --- 요청용 모델 (POST Body) ---
class ReportCreate(BaseModel):
    type: HazardType = Field(..., description="Type of hazard")
    description: str = Field(..., max_length=200, description="Short description of the hazard")
    location: GeoJSONPoint
    photoUrls: Optional[List[str]] = Field(None, description="Optional photo URLs")
    detectedAt: Optional[datetime] = Field(None, description="Time when hazard was detected")
    severity: Severity = Field("medium", description="Severity level (low/medium/high)")
    status: Status = Field("pending_review", description="Current review status")

    # 스키마 예시를 보여주기 위한 설정
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "sidewalk_damage",
                "description": "보도블록이 심하게 파손되어 휠체어 이동이 어렵습니다.",
                "location": {"type": "Point", "coordinates": [127.043, 37.501]},
                "severity": "high"
            }
        }
    )

# --- 응답용 모델 (Response) ---
class ReportResponse(ReportCreate):
    id: Optional[PyObjectId] = Field(
        None,
        alias="_id",
        description="Unique identifier (MongoDB ObjectId)"
    )

    createdAt: datetime = Field(..., description="Timestamp when report was created")

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
