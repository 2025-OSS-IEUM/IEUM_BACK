from fastapi import FastAPI, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

# (1) Pydantic 모델
from .models import UserIn, UserInDB

# (2) 라우터 추가
from .routers import reports

# 환경 변수 로드
load_dotenv()

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# MongoDB 연결
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_database("ieum_db")
users_collection = db.get_collection("users")

@app.on_event("startup")
async def startup_event():
    print("FastAPI 애플리케이션 시작")
    try:
        await client.admin.command('ping')
        print("MongoDB 연결 성공")
    except Exception as e:
        print(f"MongoDB 연결 실패: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    print("FastAPI 애플리케이션 종료")
    client.close()

@app.get("/")
def read_root():
    return {"message": "IEUM API v1 (FastAPI + MongoDB)"}

@app.get("/internal/health")
async def health_check():
    try:
        await client.admin.command('ping')
        db_status = "ok"
    except Exception as e:
        db_status = f"failed: {e}"
    return {"status": "ok", "details": {"db_connection": db_status}}

# --- /auth/signup ---
@app.post("/auth/signup", response_model=UserInDB, status_code=status.HTTP_201_CREATED, tags=["Auth"])
async def signup(user_in: UserIn):
    # 아이디 중복 확인
    existing_user = await users_collection.find_one({"username": user_in.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 아이디입니다."
        )

    # 이메일 중복 확인
    existing_email = await users_collection.find_one({"email": user_in.email})
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 가입된 이메일 주소입니다."
        )

    # 비밀번호 해싱
    hashed_password = pwd_context.hash(user_in.password)

    # DB에 저장할 데이터 구성
    user_data = user_in.dict(exclude={"password"})
    user_data["hashed_password"] = hashed_password
    new_user = UserInDB(**user_data)

    # MongoDB에 삽입
    result = await users_collection.insert_one(new_user.dict(by_alias=True))
    if not result.inserted_id:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="사용자 생성 실패")

    # 삽입된 사용자 문서 조회
    created_user = await users_collection.find_one({"_id": result.inserted_id})
    if not created_user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="생성된 사용자 조회 실패")

    # 반환 (UserInDB alias 자동 매핑)
    return UserInDB(**created_user)

# --- reports 라우터 등록 ---
app.include_router(reports.router)

print("[api/main.py] /auth/signup + /reports 등록 완료")
