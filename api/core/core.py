# api/core/core.py

import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# .env 로드
load_dotenv()


# ---------------------------------------------------
# 1. 환경 변수 (보안 & DB 설정)
# ---------------------------------------------------
MONGO_URI = os.getenv("MONGO_URI")
SECRET_KEY = os.getenv("SECRET_KEY", "your-fallback-secret-key-please-change")
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60     # 1시간
REFRESH_TOKEN_EXPIRE_DAYS = 14       # 14일


# ---------------------------------------------------
# 2. MongoDB 연결 설정 (필수 값 체크)
# ---------------------------------------------------
if not MONGO_URI:
    raise RuntimeError("❌ MONGO_URI is missing in the .env file.")


client = AsyncIOMotorClient(MONGO_URI)
db = client.get_database("ieum_db")
users_collection = db.get_collection("users")
