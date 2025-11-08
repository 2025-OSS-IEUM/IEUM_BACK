# app/routers/auth.py

from fastapi import APIRouter

router = APIRouter(
    prefix="/api/auth",
    tags=["Auth"],
)

# [수업 자료 활용 1: 일급 함수 (05.First-Class Functions.pdf)]
#
# [cite_start]파이썬의 함수는 '일급 객체(First-Class Object)'입니다[cite: 31].
# [cite_start]즉, 변수에 할당하거나, 다른 함수의 인수로 전달할 수 있습니다[cite: 36, 37].
#
# 여기서 정의한 `register_user` 함수는 그 자체로 '일급 객체'입니다.
# 이 함수는 바로 실행되지 않고, `@router.post("/register")`라는
# '고차 함수(데코레이터)'에 인수로 전달됩니다.
@router.post("/register")
async def register_user():
    # TODO: A-1단계의 Person 3이 로직 구현
    return {"message": "회원가입 API (구현 예정)"}


@router.post("/login")
async def login_user():
    # TODO: A-1단계의 Person 1이 JWT 발급 구현
    return {"message": "로그인 API (구현 예정)"}