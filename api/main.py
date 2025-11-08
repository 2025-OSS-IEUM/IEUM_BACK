# api/main.py
from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

# .env 파일 로드 (docker-compose가 아닌 로컬에서 직접 실행 시 필요)
load_dotenv()

app = FastAPI()

# MongoDB 연결 설정
# docker-compose의 .env 파일에 정의된 URI를 읽어옵니다.
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_database() # .env의 ieum_db에 연결됩니다.

@app.on_event("startup")
async def startup_event():
    print("FastAPI 애플리케이션 시작")
    try:
        # (수업 자료 02. 들어가며.pdf) Pydantic 모델처럼 FastAPI는
        # 시작/종료 이벤트를 데코레이터로 쉽게 관리합니다.
        await client.admin.command('ping')
        print("✅ MongoDB 연결 성공")
    except Exception as e:
        print(f"❌ MongoDB 연결 실패: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    print("FastAPI 애플리케이션 종료")
    client.close()

@app.get("/")
def read_root():
    # (수업 자료 04. 딕셔너리) 
    # Python 딕셔너리를 반환하면 FastAPI가 자동으로 JSON 응답으로 변환합니다.
    return {"message": "IEUM API v1 (FastAPI + MongoDB)"}

@app.get("/internal/health")
async def health_check():
    """
    (API 명세서 16번 내부 헬스체크 참고)
    DB 연결 상태를 포함한 헬스 체크 엔드포인트입니다.
    """
    try:
        await client.admin.command('ping')
        db_status = "ok"
    except Exception as e:
        db_status = f"failed: {e}"

    return {
        "status": "ok",
        "details": {
            "db_connection": db_status
        }
    }