# api/core.py

import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# .env 로드
load_dotenv()

# ================================
# 1. 환경 변수 로드
# ================================
MONGO_URI = os.getenv("MONGO_URI")
SECRET_KEY = os.getenv("SECRET_KEY", "your-fallback-secret-key-please-change")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60   # 1시간
REFRESH_TOKEN_EXPIRE_DAYS = 14     # 14일

# ================================
# 2. MongoDB 연결
# ================================
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_database("ieum_db")

# 컬렉션 객체
users_collection = db.get_collection("users")
reports_collection = db.get_collection("hazard_reports")


# ================================
# 3. 인덱스 설정 함수 (startup에서 호출)
# ================================
async def create_indexes():
    print("📌 MongoDB 인덱스 설정 시작")

    # Users Collection
    await users_collection.create_index("username", unique=True)
    await users_collection.create_index("email", unique=True)
    await users_collection.create_index("createdAt")

    # Password reset용
    await users_collection.create_index("passwordResetCode")
    await users_collection.create_index("passwordResetExpires")

    # Reports Collection
    await reports_collection.create_index("userId")
    await reports_collection.create_index("createdAt")

    # Geo Index (Hazard Reports - 지도 기능 대비)
    try:
        await reports_collection.create_index(
            [("location", "2dsphere")]
        )
        print("🌍 Geo Index(2dsphere) 생성 완료")
    except Exception as e:
        print(f"⚠️ Geo 인덱스 생성 실패: {e}")

    print("✅ 모든 인덱스 생성 완료!")