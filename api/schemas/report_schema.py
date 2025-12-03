from pydantic import BaseModel, Field, ConfigDict, BeforeValidator
from typing import List, Optional, Literal, Annotated
from datetime import datetime

# ObjectId를 문자열로 자동 변환하기 위한 유틸리티 타입
PyObjectId = Annotated[str, BeforeValidator(str)]

# --- 공통 Enum 정의 ---
HazardType = Literal[
    "sidewalk_damage", "construction", "missing_crosswalk", "no_tactile", "etc"
]

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
    type: HazardType
    description: str = Field(..., max_length=200)
    location: GeoJSONPoint

    # 🔥 키 생략 가능 + 값 없어도 OK
    photoUrls: Optional[List[str]] = Field(default=None)
    detectedAt: Optional[datetime] = Field(default=None)

    # 🔥 severity는 숫자 고정 (1~5)
    severity: int = Field(
        3,
        ge=1,
        le=5,
        description="Severity level as integer (1~5)"
    )

    status: Status = "pending_review"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "type": "sidewalk_damage",
                "description": "보도블록이 심하게 파손되어 휠체어 이동이 어렵습니다.",
                "location": {"type": "Point", "coordinates": [127.043, 37.501]},
                "severity": 3,
                "photoUrls": ["file://example.jpg"],
                "detectedAt": None
            }
        }
    )


# --- 응답용 모델 ---
class ReportResponse(ReportCreate):
    id: Optional[PyObjectId] = Field(None, alias="_id")
    user_id: str
    createdAt: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )
