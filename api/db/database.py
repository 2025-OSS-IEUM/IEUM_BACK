# (FIXED) Use 'motor' for async operations, not 'pymongo'
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings # .env 값을 읽어온 settings 객체 사용

# MongoDB 연결 (비동기 클라이언트)
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
reports_collection = db["hazard_reports"]