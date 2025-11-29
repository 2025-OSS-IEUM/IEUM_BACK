# (FIXED) Use 'motor' for async operations, not 'pymongo'
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings # .env 값을 읽어온 settings 객체 사용
from pymongo import GEOSPHERE, ASCENDING # 👈 인덱스 생성을 위해 임포트
from typing import List, Dict, Any # 👈 타입 힌팅을 위해 임포트

# --- MongoDB 연결 (비동기 클라이언트) ---
# (참고: client 객체는 main.py의 startup_event에서 실제 연결을 테스트합니다.)
client = AsyncIOMotorClient(settings.MONGO_URI)

# DB 핸들 가져오기
# (settings.DB_NAME은 .env 파일의 'ieum' 값입니다)
db = client.get_database(settings.DB_NAME)

# --- 컬렉션 핸들 준비 ---

# (1) Users Collection
users_collection = db.get_collection("users")

# (2) Reports Collection (FIXED:  누락되었던 컬렉션 추가)
reports_collection = db.get_collection("hazard_reports")

print(f"[api/db/database.py] MongoDB 클라이언트 초기화 완료. (DB: {settings.DB_NAME})")

# ===================================================================
# 🔽 (추가된 함수 1) 인덱스 생성
# ===================================================================
async def create_db_indexes():
    """
    애플리케이션 시작 시(main.py) 호출되어
    필수적인 DB 인덱스를 생성합니다.
    """
    print("Checking and creating database indexes...")
    try:
        # (A) Hazard Reports 컬렉션 (공간 인덱스)
        #    -> ST_DWithin (PostGIS) 기능을 위해 'location' 필드에 2dsphere
        await reports_collection.create_index([("location", GEOSPHERE)])
        print("-> 'hazard_reports': 2dsphere index on 'location' ensured.")
        
        # (B) Users 컬렉션 (고유 인덱스)
        #    -> user_model.py에서 계획한 대로
        await users_collection.create_index([("user_id", ASCENDING)], unique=True)
        await users_collection.create_index([("email", ASCENDING)], unique=True)
        await users_collection.create_index([("username", ASCENDING)], unique=True)
        print("-> 'users': Unique indexes on 'user_id', 'email', 'username' ensured.")
        
    except Exception as e:
        print(f"[IndexError] Failed to create DB indexes: {e}")

# ===================================================================
# 🔽 (추가된 함수 2) 공간 쿼리 (ST_DWithin 대체)
# ===================================================================
async def find_hazards_near_coordinates(
    coordinates: List[float],    # [경도(lon), 위도(lat)]
    max_distance_meters: int = 50, # 검색 반경 (미터)
    limit: int = 10                # 최대 검색 개수
) -> List[Dict[str, Any]]:
    """
    특정 좌표(lon, lat) 주변의 승인된(approved) 위험 요소를 검색합니다.
    (MongoDB의 $nearSphere 쿼리 사용)
    """
    query = {
        "status": "approved", # 승인된 제보만 조회
        "location": {
            "$nearSphere": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": coordinates # 👈 수정된 리스트 사용!
                },
                "$maxDistance": max_distance_meters # 미터 단위
            }
        }
    }
    
    # (성능 최적화: 필요한 필드만 가져오기)
    projection = {
        "type": 1,       # ReportCreate 스키마의 'type'
        "severity": 1,   # ReportCreate 스키마의 'severity'
        "_id": 0
    }
    print(f"DEBUG QUERY: {query}")

    try:
        hazards_cursor = reports_collection.find(query, projection).limit(limit)
        results = await hazards_cursor.to_list(length=limit)
        print(f"DEBUG HAZARD COUNT: {len(results)}")
        return results
    
    except Exception as e:
        print(f"Error during hazard query: {e}")
        return []