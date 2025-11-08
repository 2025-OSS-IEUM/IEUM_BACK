from fastapi import FastAPI, HTTPException, status # HTTPException, status 추가
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from app.routers import auth  # 라우터 추가

# (수업 자료 02) 우리가 방금 설계한 Pydantic '데이터 모델'을 임포트
from .models import UserIn, UserInDB

# (비밀번호 해싱용)
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# .env 파일 로드
load_dotenv()

app = FastAPI()

# MongoDB 연결 설정
MONGO_URI = os.getenv("MONGO_URI")
client = AsyncIOMotorClient(MONGO_URI)
db = client.get_database("ieum_db") # .env의 DB 이름과 일치
users_collection = db.get_collection("users") # 'users' 컬렉션(테이블) 사용

# Auth 라우터 연결
app.include_router(auth.router)

@app.on_event("startup")
async def startup_event():
    print("FastAPI 애플리케이션 시작")
    try:
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

# --- (여기서부터 '사람1'이 '사람2'를 위해 만든 뼈대) ---

@app.post("/auth/signup", 
          response_model=UserInDB, # 응답은 UserInDB 모델 형식을 따름
          status_code=status.HTTP_201_CREATED, # 성공 시 201 상태 코드 반환
          tags=["Auth"]) # (API 문서용 태그)
async def signup(user_in: UserIn):
    """
    (API 명세서 1. (1) 회원 가입)
    (수업 자료 02, 04) Pydantic(UserIn) 모델로 Request Body(JSON 딕셔너리)를 검증.
    """
    
    # (API 명세서 1. (17) 아이디 중복 확인)
    existing_user = await users_collection.find_one({"username": user_in.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, # (API 명세서 409)
            detail="이미 사용 중인 아이디입니다."
        )
    
    # (API 명세서 1. (18) 이메일 중복 확인)
    existing_email = await users_collection.find_one({"email": user_in.email})
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, # (API 명세서 409)
            detail="이미 가입된 이메일 주소입니다."
        )

    # (중요) 비밀번호를 평문으로 저장하면 안 됨! 해싱(암호화)
    hashed_password = pwd_context.hash(user_in.password)
    
    # (수업 자료 04) Pydantic 모델(dict)을 기반으로 DB에 저장할 딕셔너리 생성
    user_data = user_in.dict(exclude={"password"}) # 원본 비번 제외
    user_data["hashed_password"] = hashed_password
    
    # UserInDB 모델로 감싸서 기본값(createdAt, accessibility) 생성
    new_user = UserInDB(**user_data)
    
    # MongoDB는 딕셔너리 형태로 데이터를 저장 (by_alias=True로 id -> _id 변환)
    result = await users_collection.insert_one(new_user.dict(by_alias=True))
    
    # 방금 삽입된 사용자 정보 반환 (ID 포함)
    created_user = await users_collection.find_one({"_id": result.inserted_id})
    
    # (수업 자료 02) Pydantic 모델로 변환하여 API 명세서에 맞는 JSON 응답 반환
    return UserInDB(**created_user)

print("✅ [api/main.py] /auth/signup 뼈대 엔드포인트 추가 완료")