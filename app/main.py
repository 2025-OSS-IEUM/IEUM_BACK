# app/main.py

from fastapi import FastAPI
from app.routers import auth 

# [DB 연동을 위한 추가]
from app.db.session import engine     # 1. session.py에서 engine을 가져옵니다.
from app.models import user         # 2. user.py 모델을 가져옵니다. (중요!)

# 3. 개발 환경에서 앱 시작 시 테이블을 생성합니다.
#    (User 클래스에서 Base를 상속받았기 때문에, Base가 User 테이블을 인식합니다)
# [수업 자료 활용 3: 모듈 임포트 (04.데이터구조체-dictionary-sets.pdf)]
#    - '04.데이터구조체' 13페이지 예제 2처럼
#      import sys, re를 하듯, 우리가 만든 모듈(user, engine)을 import해서 사용합니다.
user.Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="IEUM_BACK (안전 길찾기 API)",
    description="보행 약자를 위한 안전 길찾기 서비스 백엔드 API",
    version="v1"
)

app.include_router(auth.router)

@app.get("/")
async def root():
    return {"message": "Welcome to IEUM_BACK API Server!"}