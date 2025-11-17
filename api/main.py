from routers import internal 
from fastapi import FastAPI
from db.database import client, users_collection, create_db_indexes # DB 객체
from routers import auth, reports, users         # 라우터 임포트
from routers import route
from routers import safe_route         # D 뼈대

app = FastAPI()

# -------------------------
# 라우터 등록
# -------------------------
app.include_router(auth.router)
app.include_router(reports.router)
app.include_router(users.router)
app.include_router(route.router)
app.include_router(internal.router)     
app.include_router(safe_route.router)   # D 뼈대

# 라우터 등록 필수입니다

# ---------------------------------
# 🔥 애플리케이션 시작 이벤트
# ---------------------------------
@app.on_event("startup")
async def startup_event():
    print("FastAPI 애플리케이션 시작")

    if client is None:
        print("❌ MongoDB 클라이언트가 초기화되지 않았습니다.")
        return

    try:
        # 연결 테스트
        await client.admin.command("ping")
        print("✅ MongoDB 연결 성공")

        if users_collection is None:
            print("❌ users 컬렉션이 초기화되지 않았습니다.")
            return

        await create_db_indexes()

    except Exception as e:
        print(f"❌ MongoDB 연결 또는 인덱스 설정 실패: {e}")


# ---------------------------------
# 🔥 애플리케이션 종료 이벤트
# ---------------------------------
@app.on_event("shutdown")
async def shutdown_event():
    print("FastAPI 애플리케이션 종료")
    if client is not None:
        client.close()


# -------------------------
# 기본 라우트
# -------------------------
@app.get("/")
def read_root():
    return {"message": "IEUM API v1 (FastAPI + MongoDB)"}


@app.get("/internal/health")
async def health_check():
    """DB 연결 상태를 포함한 서버 헬스 체크"""
    db_status = "unknown"

    if client is None:
        db_status = "client not initialized"
    else:
        try:
            await client.admin.command("ping")
            db_status = "ok"
        except Exception as e:
            db_status = f"failed: {e}"

    return {
        "status": "ok",
        "details": {"db_connection": db_status}
    }


print("[api/main.py] FastAPI 앱 초기화 완료. 라우터 로드됨.")
