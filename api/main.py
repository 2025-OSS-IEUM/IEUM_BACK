from fastapi import FastAPI

# 1. 라우터 임포트 (app/routers/auth.py)
from app.routers import auth 

# 2. 공통 모듈 임포트 (api/core.py)
# (DB 연결/종료 이벤트 및 헬스 체크용)
from .core import client, users_collection

app = FastAPI()

# 3. 라우터 연결
app.include_router(auth.router)


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 MongoDB 연결 및 인덱스 설정"""
    print("FastAPI 애플리케이션 시작")
    try:
        # core.py의 client 사용
        await client.admin.command('ping')
        print("✅ MongoDB 연결 성공")
        
        # core.py의 users_collection 사용
        await users_collection.create_index("username", unique=True)
        await users_collection.create_index("email", unique=True)
        print("✅ MongoDB 'users' 컬렉션 인덱스 설정 완료")
    except Exception as e:
        print(f"❌ MongoDB 연결 또는 인덱스 설정 실패: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 MongoDB 연결 종료"""
    print("FastAPI 애플리케이션 종료")
    client.close() # core.py의 client 사용

@app.get("/")
def read_root():
    return {"message": "IEUM API v1 (FastAPI + MongoDB)"}

@app.get("/internal/health")
async def health_check():
    """DB 연결 상태를 포함한 헬스 체크"""
    try:
        await client.admin.command('ping') # core.py의 client 사용
        db_status = "ok"
    except Exception as e:
        db_status = f"failed: {e}"

    return {
        "status": "ok",
        "details": {
            "db_connection": db_status
        }
    }