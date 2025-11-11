# app/models/hazard_report.py
from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import List, Literal, Optional, Dict, Any
from datetime import datetime

HazardType = Literal[
    "sidewalk_damage", "construction", "missing_crosswalk", "no_tactile", "etc"
]
Severity = Literal["low", "medium", "high"]
Status   = Literal["pending_review", "approved", "resolved"]

class GeoJSONPoint(BaseModel):
    type: Literal["Point"] = "Point"
    coordinates: List[float] = Field(..., min_length=2, max_length=2, description="[lng, lat]")

    @field_validator("coordinates")
    @classmethod
    def lonlat(cls, v):
        lon, lat = v
        if not (-180 <= lon <= 180 and -90 <= lat <= 90):
            raise ValueError("coordinates must be [lng, lat] in valid ranges")
        return v

class HazardReportCreate(BaseModel):
    type: HazardType
    description: str = Field(..., max_length=200)
    location: GeoJSONPoint
    photoUrls: Optional[List[HttpUrl]] = None
    detectedAt: Optional[datetime] = None
    severity: Severity = "medium"
    status: Status   = "pending_review"

class HazardReportDB(HazardReportCreate):
    id: Optional[str] = None  # Mongo _id 문자열로 매핑 사용 가능
#좌표는 **GeoJSON Point: [lng, lat]**로 고정.
#2dsphere 인덱스는 이 필드(location)에 걸린다.
