from fastapi import FastAPI, HTTPException, status
from db.database import client, users_collection # DB 객체 임포트
from routers import auth, reports # 라우터 임포트

# -- FastAPI 앱 생성 --
app = FastAPI()

# -- 라우터 연결 --
# (참고: auth.router에 /auth/signup 등이 이미 포함되어 있습니다)
app.include_router(auth.router)
app.include_router(reports.router)

# -- 공통 이벤트 핸들러 --

@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 MongoDB 연결 및 인덱스 설정"""
    print("FastAPI 애플리케이션 시작")
    if not client:
        print("❌ MongoDB 클라이언트가 초기화되지 않았습니다. (db/database.py 확인)")
        return
        
    try:
        await client.admin.command('ping')
        print("✅ MongoDB 연결 성공")
        
        if not users_collection:
            print("❌ MongoDB 'users' 컬렉션이 초기화되지 않았습니다. (db/database.py 확인)")
            return

        # 'users' 컬렉션 인덱스 설정
        await users_collection.create_index("username", unique=True)
        await users_collection.create_index("email", unique=True)
        print("✅ MongoDB 'users' 컬렉션 인덱스 설정 완료")
    except Exception as e:
        print(f"❌ MongoDB 연결 또는 인덱스 설정 실패: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 MongoDB 연결 종료"""
    print("FastAPI 애플리케이션 종료")
    if client:
        client.close()

# -- 기본 라우트 --

@app.get("/")
def read_root():
    return {"message": "IEUM API v1 (FastAPI + MongoDB)"}

@app.get("/internal/health")
async def health_check():
    """DB 연결 상태를 포함한 헬스 체크"""
    db_status = "unknown"
    if not client:
        db_status = "client not initialized"
    else:
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

print("[api/main.py] FastAPI 앱 초기화 완료. 라우터 로드됨.")