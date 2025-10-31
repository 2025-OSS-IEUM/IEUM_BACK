# api/main.py

# --- 1. 라이브러리 불러오기 ---

# FastAPI: 웹 서버를 만드는 데 필요한 핵심 라이브러리
from fastapi import FastAPI
# httpx: 카카오 API처럼 다른 웹사이트(API)에 요청을 보낼 때 쓰는 라이브러리
import httpx
# os: '운영 체제(Operating System)' 기능, KAKAO_API_KEY 같은 '환경 변수'를 읽을 때 사용
import os
# E 작업을 위해 Pydantic 모델과 타입 힌트를 가져옵니다.
from pydantic import BaseModel
from typing import List, Optional, Any 

# --- 2. FastAPI 앱 생성 ---

# app이라는 이름으로 FastAPI 앱(서버)을 만듭니다. 이게 우리 서버의 본체입니다.
app = FastAPI()

# --- 3. 카카오 API 키 설정 ---

# os.getenv("KAKAO_API_KEY", "...")
# 1. (권장) 'KAKAO_API_KEY'라는 이름의 '환경 변수'가 설정되어 있으면 그 값을 가져옵니다.
# 2. (임시) 만약 환경 변수가 없으면, "..."에 있는 하드코딩된 키 값을 대신 사용합니다.
KAKAO_API_KEY = os.getenv("KAKAO_API_KEY", "054ca149348d54725291a60021b90663") 

# --- E 작업 (응답 포맷 정의) ---
# 1. 우리가 반환할 응답의 '틀'을 Pydantic 모델로 만듭니다.

class Step(BaseModel):
    """
    경로의 각 단계별 안내 (카카오 'guides'에 해당)
    """
    name: str      # 안내 문구 (예: "우회전")
    distance: int  # 해당 구간 거리 (미터)
    duration: int  # 해당 구간 소요 시간 (초)

class OurRoute(BaseModel):
    """
    우리가 정의한 단일 경로 포맷
    """
    summary: dict                   # 요약 정보 (카카오 'summary' 원본)
    # GeoJSON 호환을 위해 [경도, 위도] 리스트의 리스트로 변경
    polyline: List[List[float]]     
    steps: List[Step]               # 경로 단계별 안내
    # Task D를 위한 필드 (지금은 빈 리스트로 반환)
    hazards_on_path: List[Any]      

class RouteResponse(BaseModel):
    """
    /route의 최종 응답 포맷.
    'alternatives' 필드에 경로 후보 2~3개가 OurRoute 리스트로 담깁니다.
    """
    alternatives: List[OurRoute]


# --- 4. C/E 작업: '/route' 엔드포인트(API 주소) 만들기 ---

# @app.get("/route"): 
#   FastAPI에게 'GET' 방식의 HTTP 요청을 /route 주소로 받겠다고 알립니다.
#   E 작업을 위해 response_model (응답 모델)을 우리가 정의한 RouteResponse로 지정합니다.
@app.get("/route", response_model=RouteResponse)
# async def ...: 
#   /route로 요청이 들어오면 이 함수가 실행됩니다. 'async'는 httpx가 비동기로 작동하기 위해 필요합니다.
# (start_lon: float, ...): 
#   GET 요청의 '쿼리 파라미터'(예: ?start_lon=127.123)를 자동으로 받아서 변수에 넣어줍니다.
# E 작업을 위해 'pref' 파라미터를 추가합니다. (기본값 "balanced")
async def get_route(
    start_lon: float, 
    start_lat: float, 
    end_lon: float, 
    end_lat: float,
    pref: Optional[str] = "balanced" # E 스펙: pref=safe|balanced|fast 지원
):
    
    # 카카오 길찾기 API가 요청을 받는 공식 주소입니다.
    kakao_url = "https://apis-navi.kakaomobility.com/v1/directions"
    
    # 카카오 API에 보낼 '파라미터'들을 딕셔너리(Key-Value) 형태로 정리합니다.
    params = {
        # 함수로 받은 출발지 좌표를 "경도,위도" 형식의 문자열로 만듭니다.
        "origin": f"{start_lon},{start_lat}",
        # 함수로 받은 도착지 좌표를 "경도,위도" 형식의 문자열로 만듭니다.
        "destination": f"{end_lon},{end_lat}",
        # C 작업의 핵심! 'True'로 설정해야 대안 경로(후보 2~3개)를 같이 보내줍니다.
        "alternatives": True,
        # TODO: 'pref' 값(safe/balanced/fast)에 따라
        # 카카오의 'priority' 옵션(RECOMMEND, TIME, FREE)을 매핑할 수 있습니다.
    }
    
    # 카카오 API에 보낼 '헤더'입니다. (요청의 메타데이터)
    headers = {
        # "Authorization": "저 인증된 사용자입니다"라고 알려주는 부분. 
        # 우리가 발급받은 KAKAO_API_KEY를 'KakaoAK [키]' 형식으로 보냅니다.
        "Authorization": f"KakaoAK {KAKAO_API_KEY}",
        # "Content-Type": "요청/응답 데이터 형식은 JSON입니다"라고 알려줍니다.
        "Content-Type": "application/json"
    }
    
    # --- 5. 카카오 API 실제 호출 ---
    
    # httpx.AsyncClient()를 client라는 이름으로 생성합니다.
    # 'async with'는 작업이 끝나면 client를 자동으로 정리(닫기)해줘서 편리합니다.
    async with httpx.AsyncClient() as client:
        # client.get(...) : 카카오 API 주소(kakao_url)로 GET 요청을 보냅니다.
        # params=params: 위에서 만든 파라미터(출발/도착지)를 쿼리 스트링으로 붙여서 보냅니다.
        # headers=headers: 위에서 만든 인증 헤더를 포함시킵니다.
        # await: 카카오가 응답을 줄 때까지 (비동기로) 기다립니다.
        response = await client.get(kakao_url, params=params, headers=headers)
        
        # --- 6. 응답 처리 (C) ---
        
        # 만약 응답 코드가 200 (성공)이 아니라면,
        if response.status_code != 200:
            # API 호출이 실패했음을 알리고, 카카오가 보내준 에러 내용을 함께 반환합니다.
            return {"error": "카카오 API 호출 실패", "details": response.json()}
        
        # 카카오가 보내준 원본 JSON 데이터를 변수에 저장합니다.
        kakao_data = response.json()

    # --- 7. E 작업: 카카오 응답을 'RouteResponse' 포맷으로 가공 ---
    
    # 가공된 OurRoute 객체들을 담을 빈 리스트를 준비합니다.
    processed_routes: List[OurRoute] = []
    
    # 카카오 응답의 'routes' 배열 (경로 후보 2~3개)을 하나씩 순회합니다.
    for route in kakao_data.get("routes", []):
        
        all_steps: List[Step] = []
        all_polyline_coords: List[List[float]] = []

        # 카카오 경로는 'sections' (구간) 리스트로 나뉘어 있습니다. (보통 1개)
        for section in route.get("sections", []):
            
            # 1. E 스펙 'steps' 만들기: 'guides'를 'Step' 모델로 변환
            for guide in section.get("guides", []):
                all_steps.append(Step(
                    name=guide.get("name", "이름 없음"),
                    distance=guide.get("distance", 0),
                    duration=guide.get("duration", 0)
                ))
            
            # 2. E 스펙 'polyline' 만들기: 'roads'의 'vertexes'를 변환
            # 카카오 폴리라인은 [lon1, lat1, lon2, lat2, ...] 형식입니다.
            raw_vertexes = []
            for road in section.get("roads", []):
                raw_vertexes.extend(road.get("vertexes", []))
            
            # GeoJSON 호환 형식 [[lon1, lat1], [lon2, lat2], ...]으로 변환
            all_polyline_coords = [
                [raw_vertexes[i], raw_vertexes[i+1]] 
                for i in range(0, len(raw_vertexes), 2)
            ]

        # E 스펙에 맞춘 'OurRoute' 객체 생성
        our_route_object = OurRoute(
            summary=route.get("summary", {}), # 카카오 'summary' 원본 사용
            polyline=all_polyline_coords,      # 우리가 가공한 폴리라인
            steps=all_steps,                   # 우리가 가공한 스텝
            hazards_on_path=[]                 # Task D에서 구현 (지금은 빈 리스트)
        )
        processed_routes.append(our_route_object)

    # 최종적으로 E에서 정의한 'RouteResponse' 포맷으로 반환
    return RouteResponse(alternatives=processed_routes)
