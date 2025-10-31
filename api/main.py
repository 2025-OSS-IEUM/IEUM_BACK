# api/main.py

from fastapi import FastAPI
import httpx
import os
# from pydantic import BaseModel  <- GET 방식은 BaseModel이 필요 없습니다.

app = FastAPI()

KAKAO_API_KEY = os.getenv("KAKAO_API_KEY", "054ca149348d54725291a60021b90663") # 키는 그대로 두세요

# 1. Pydantic 모델이 필요 없습니다.


# 2. C 작업 엔드포인트 수정
# @app.post("/api/get-kakao-routes") -> @app.get("/route")로 변경
# (request: RouteRequest) -> (start_lon: float, ...) 쿼리 파라미터로 변경
@app.get("/route")  # <-- 팀에서 정한 엔드포인트
async def get_route(start_lon: float, start_lat: float, end_lon: float, end_lat: float):
    
    kakao_url = "https://apis-navi.kakaomobility.com/v1/directions"
    
    params = {
        # 쿼리 파라미터로 받은 값을 그대로 사용
        "origin": f"{start_lon},{start_lat}",
        "destination": f"{end_lon},{end_lat}",
        "alternatives": True,
    }
    
    headers = {
        "Authorization": f"KakaoAK {KAKAO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(kakao_url, params=params, headers=headers)
        
        if response.status_code != 200:
            return {"error": "카카오 API 호출 실패", "details": response.json()}
        
        return response.json()