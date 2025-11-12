import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# .env 로드
load_dotenv()

# --- 1. 환경 변수 (설정값) ---
# DB와 JWT(보안)에 필요한 설정값을 .env에서 읽어옵니다.
MONGO_URI = os.getenv("MONGO_URI")
SECRET_KEY = os.getenv("SECRET_KEY", "your-fallback-secret-key-please-change")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1시간
REFRESH_TOKEN_EXPIRE_DAYS = 14    # 14일

# --- 2. MongoDB 연결 설정 ---
# 이 객체들을 다른 파일(main.py, routers/auth.py 등)에서 import해서 사용합니다.
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_database("ieum_db")
users_collection = db.get_collection("users")