# (FIXED) Use 'motor' for async operations, not 'pymongo'
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings
from pymongo import GEOSPHERE, ASCENDING
from typing import List, Dict, Any

# --------------------------------------------
# MongoDB 연결 (비동기 클라이언트)
# --------------------------------------------
client = AsyncIOMotorClient(settings.MONGO_URI)
db = client.get_database(settings.DB_NAME)

# --------------------------------------------
# 컬렉션 핸들
# --------------------------------------------
users_collection = db.get_collection("users")

# ✔ hazard_reports — 유저 신고가 저장되는 곳
reports_collection = db.get_collection("hazard_reports")

print(f"[api/db/database.py] MongoDB Ready (DB: {settings.DB_NAME})")

# --------------------------------------------
# 인덱스 생성 (앱 시작 시 1회 실행)
# --------------------------------------------
async def create_db_indexes():
    print("Checking and creating database indexes...")

    try:
        # (A) 공간 인덱스 — 위치 기반 조회 필수
        await reports_collection.create_index([("location", GEOSPHERE)])

        # (B) Users 컬렉션 고유 인덱스
        await users_collection.create_index([("user_id", ASCENDING)], unique=True)
        await users_collection.create_index([("email", ASCENDING)], unique=True)
        await users_collection.create_index([("username", ASCENDING)], unique=True)

        print("-> Indexes created successfully.")

    except Exception as e:
        print(f"[IndexError] Failed to create DB indexes: {e}")

# --------------------------------------------
# 주변 위험 요소 조회 (ST_DWithin 대체)
# --------------------------------------------
async def find_hazards_near_coordinates(
    coordinates: List[float],
    max_distance_meters: int = 50,
    limit: int = 10
) -> List[Dict[str, Any]]:

    query = {
        "status": "approved",
        "location": {
            "$nearSphere": {
                "$geometry": {
                    "type": "Point",
                    "coordinates": coordinates
                },
                "$maxDistance": max_distance_meters
            }
        }
    }

    projection = {
        "type": 1,
        "severity": 1,
        "_id": 0
    }

    try:
        cursor = reports_collection.find(query, projection).limit(limit)
        results = await cursor.to_list(length=limit)
        return results

    except Exception as e:
        print(f"Error during hazard query: {e}")
        return []
