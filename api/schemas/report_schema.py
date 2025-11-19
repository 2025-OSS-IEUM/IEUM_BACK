from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

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

# --- 응답용 모델 (Response) ---
class ReportResponse(ReportCreate):
    id: str = Field(..., description="Unique identifier (MongoDB ObjectId)")
    createdAt: datetime = Field(..., description="Timestamp when report was created")