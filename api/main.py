from fastapi import FastAPI, HTTPException, status
import os
from dotenv import load_dotenv
from passlib.context import CryptContext
from motor.motor_asyncio import AsyncIOMotorClient

# 1. 라우터 임포트
from api.routers import auth
from api.routers import reports

# 2. 공통 모듈 (DB)
from api.core import client, users_collection

# 3. Pydantic 모델
from api.models import UserIn, UserInDB

from api.core import create_indexes

# 환경 변수 로드
load_dotenv()

app = FastAPI(
    title="IEUM API",
    version="1.0.0"
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB URI
MONGO_URI = os.getenv("MONGO_URI")


# -------------------------------------------------------
# 🟦 서버 시작 이벤트
# -------------------------------------------------------

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 MongoDB 연결 및 인덱스 설정"""
    print("🚀 FastAPI 애플리케이션 시작")

    try:
        # 연결 테스트
        await client.admin.command('ping')
        print("✅ MongoDB 연결 성공")

        # 🔥 딱 이 한 줄만 넣으면 됨 (전체 인덱스 자동 생성)
        await create_indexes()

    except Exception as e:
        print(f"❌ MongoDB 연결/인덱스 설정 실패: {e}")

# -------------------------------------------------------
# 🟥 서버 종료 이벤트
# -------------------------------------------------------
@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 MongoDB 연결 종료"""
    print("🛑 FastAPI 애플리케이션 종료")
    client.close()


# -------------------------------------------------------
# 🟩 루트 엔드포인트
# -------------------------------------------------------
@app.get("/")
def read_root():
    return {"message": "IEUM API v1 (FastAPI + MongoDB)"}


# -------------------------------------------------------
# 🟨 내부 헬스 체크
# -------------------------------------------------------
@app.get("/internal/health")
async def health_check():
    """DB 연결 상태 확인"""
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


# -------------------------------------------------------
# ❌ (삭제됨) /auth/signup  
# ↳ signup은 routers/auth.py 에 있음
# -------------------------------------------------------

# -------------------------------------------------------
# 🟦 라우터 등록
# -------------------------------------------------------
app.include_router(auth.router)
app.include_router(reports.router)

print("[api/main.py] /auth/* + /reports 라우터 등록 완료")
