from pydantic import BaseModel
from typing import List, Optional


class RouteRequest(BaseModel):
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    alternatives: Optional[bool] = True


class RoutePoint(BaseModel):
    lat: float
    lon: float


class RouteOption(BaseModel):
    distance: int
    duration: int
    path: List[RoutePoint]


class RouteResponse(BaseModel):
    routes: List[RouteOption]
