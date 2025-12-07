# 이음

2025 오픈소스SW프로그래밍 - 이동약자를 위한 안전 보행 네비게이션 서비스
> **시각장애인의 안전한 이동권을 보장하는 보행 내비게이션 서비스**  
> 단순한 ‘최단 거리’가 아닌, **‘가장 안전한 길’을 안내합니다.**

---

## 💡 프로젝트 개요

단순한 거리·시간 기준의 경로 안내가 아닌,  
**파손·급경사·공사 구간·혼잡 행사 장소 등을 회피하여 안전 경로**를 안내합니다.

또한, 화면을 직접 보지 않아도 사용할 수 있도록  
**음성 안내(Voice Guide)** 및 **보이스오버 접근성(VoiceOver Accessibility)**, **방향 안내 및 햅틱 나침반**기능을 지원합니다.

---

## 🚨 서비스 필요성

| 기존 지도 앱의 한계 | SafeRoute의 해결 방식 |
|------------------|---------------------|
| 최단거리 위주 안내 → 위험 구간 미반영 | 안전요소 기반 경로 탐색 |
| 불필요한 음성 정보 과다 | 핵심 정보만 간결하게 제공 |
| 접근성 부족 | VoiceOver 및 음성 제어 완전 지원 |

> 이동권은 누구에게나 **보장받아야 할 권리**입니다.  
> 이음은 시각장애인의 **자유롭고 안전한 이동**을 목표로 합니다.

---

## ⚙️ 주요 기능

### 🧭 1. 안전 경로 탐색
- 최단 거리/시간보다 **안전 경로 우선 탐색**
- 계단, 급경사, 공사 구간 자동 회피

### 🔊 2. 음성 안내 시스템
- 핵심 정보만 **간결하게 음성 제공**
    - 방향 전환 시점
    - 횡단보도 위치/상태
    - 목적지까지 남은 거리
- 불필요한 소음 제거 (필요한 정보만 음성 출력)

### 🦻 3. 보이스오버 & 접근성 강화
- iOS/Android 기본 보이스오버 완전 호환
- 버튼, 메뉴, 경로 UI 전면 접근성 대응

### 🏥 4. 추가 기능
- 길 찾기 방향 안내 + 햅틱 나침반 기능으로 **시각 정보 없이 손 감각으로 올바른 방향 탐색 가능**
---

## 🧩 기술 스택

| 분야 | 기술 |
|------|------|
| **Backend** | FastAPI / MongoDB / Docker / Swagger |
| **Frontend** | React Native(expo) / styled components / Axios |
| **Accessibility** | VoiceOver / TTS |

---

## 👥 팀 구성

| 역할 | 이름 | 주요 담당 |
|------|------|------------|
| 기획/PM (팀장) | **강윤서** | 전체 기획 · 데이터 연계 설계 · 발표 |
| 백엔드 | **이호민**, **송주환**, **김정우** | 공공데이터 수집/정제 · 경로 탐색 알고리즘 서버 구현 · 위험요소 탐지 알고리즘|
| 프론트엔드 | **우은식**, **강윤서** | UI 구현 · 보이스오버/음성 안내 연동 · Figma 디자인 |

---



## Commit Message Convention
> Ex) Feat(component) : 탭바 컴포넌트 구현


### Tag Name 

|Tag Name|Description|
|------|---|
|Feat|새로운 기능 추가|
|Fix|버그 수정|
|Design|UI 디자인 변경|
|Style|코드 포맷 변경|
|Refactor|코드 리팩토링|
|Comment|필요한 주석 추가 및 변경|
|Docs|문서 수정|
|Test|테스트 코드|
|Chore|빌드 업무 수정, 패키지 매니저 수정, 패키지 관리자 구성 등 기능 외 작업|
|Rename|파일 혹은 폴더명을 수정하거나 옮기는 작업|
|Remove|파일 삭제|


### Scope
|Scope|Description|
|------|---|
|view|화면 중심 관련|
|component|재사용 가능한 컴포넌트 관련|
|asset|이미지, 아이콘 추가/수정 관련|
|config|설정 파일 수정|
|resource|폰트, 로컬라이징 등 수정|

####

📁 환경 변수 설정 (중요)

이 프로젝트는 Docker + FastAPI 기반이며,
환경 변수는 반드시 .env 파일로 관리하고 git에는 포함되지 않습니다.

1) .env 파일 생성 방법

루트 디렉토리(IEUM_BACK/)에 .env 파일을 새로 만들고 아래 형식대로 작성하세요:

# MongoDB 관리자 계정
MONGO_ROOT_USER=<your_root_username>
MONGO_ROOT_PASSWORD=<your_root_password>

# MongoDB 연결 정보
DB_NAME=ieum
MONGO_URI=mongodb://<your_root_username>:<your_root_password>@mongo:27017/ieum?authSource=admin

# JWT
SECRET_KEY=<your_jwt_secret>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60


⚠️ 주의

<your_root_username> / <your_root_password> / <your_jwt_secret> 은 본인이 직접 생성

이 값들은 절대로 GitHub에 올리면 안 됨!!

🐳 백엔드 Docker 실행 방법
1. Docker 빌드 + 실행
docker compose up --build


Docker가 자동으로 두 컨테이너를 실행합니다:

컨테이너	역할
api	FastAPI 서버
db	MongoDB 서버
🌐 API 문서 접속 경로

Docker가 실행되면 아래 주소로 접속 :

http://localhost:8000/docs

http://127.0.0.1:8000/docs

둘 다 똑같이 Swagger UI가 열림.

🔍 확인용 기본 경로
GET /
→ {"message": "IEUM API v1 (FastAPI + MongoDB)"}

GET /internal/health
→ DB 연결 상태 확인 가능

IEUM_BACK/
 ├── api/
 │    ├── main.py
 │    ├── routers/
 │    ├── schemas/
 │    ├── db/
 │    ├── services/
 │    └── requirements.txt     ← 📌 여기에 들어있음
 │
 ├── Dockerfile
 ├── docker-compose.yml
 └── .env        (⚠️ 절대 git에 포함 금지)


 #####
 README 업데이트 내용 (추가 섹션)
🔧 1. Security Update: Password Hashing (bcrypt 72 bytes fix)

bcrypt는 내부적으로 최대 72 bytes까지만 처리할 수 있음.
길이가 긴 비밀번호 입력 시 발생하던 오류를 해결하기 위해
api/core/security.py 를 아래와 같이 수정함:

def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")

    # bcrypt에서 처리 가능한 최대 길이 제한 (72 bytes)
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        password = password_bytes.decode("utf-8", errors="ignore")

    return pwd_context.hash(password)

✔ 효과

bcrypt ValueError 발생 제거

긴 비밀번호도 안전하게 해시됨

docker build 후 정상 작동 확인

🗂 2. MongoDB Database 이름 통일 (ieum_db)

기존 Docker 환경에서 DB 이름이 ieum / ieum_db 로 혼재되어 있어
모든 코드 및 docker-compose 환경변수를 다음과 같이 통일함:

DB_NAME=ieum_db


FastAPI 내부에서 DB 핸들 생성:

db = client.get_database("ieum_db")

✔ 효과

DB 탐색 및 관리 일관성 확보

콘테이너/로컬 개발환경 간 불일치 제거

auth/signup 데이터 insert 정상 확인

🧩 3. Signup 스키마/로직 일관화

validation mismatch 및 스키마 불일치로 인한 422 오류를 방지하기 위해
다음 파일들의 스키마/로직을 통일함.

포함 파일:

api/schemas/auth.py

api/routers/auth.py

api/db/models/user_model.py

변경사항 요약
(1) SignupRequest

passwordConfirm 추가

consent.terms, consent.privacy required

password 일치 validator 추가

(2) DB 저장 모델(User)

DB에는 절대 다음 필드를 저장하지 않음:

password

passwordConfirm

저장은 아래 필드만:

{
  "username": "...",
  "email": "...",
  "hashed_password": "...",
  "name": "...",
  "disabilityType": "...",
  "is_active": true,
  "createdAt": "...",
  "updatedAt": "..."
}

🚀 4. Docker 배포 시 주의사항
코드 변경이 있을 경우 반드시 재빌드 필요

아래 파일이 변경되면 반드시 재빌드 해야 함:

api/core/security.py

api/schemas/*

api/routers/*

api/db/*

requirements.txt

Dockerfile

재빌드 명령어
docker compose down
docker compose up --build -d

⭐ 요약 (README용 문장)

비밀번호 hashing 개선(bcrypt 72 bytes 대응), MongoDB DB 이름 통일(ieum_db),
Signup 요청/응답 스키마 정리, Docker 재빌드시 적용됨.
코드 변경 후에는 반드시 docker compose up --build -d 로 재빌드 필요.

----

🎯 개발 방향성 (간단 설명)

Schema: API 요청/응답용 (필드명은 API 친화적)

Model(DB): MongoDB 저장 구조용 (필드명, 타입 자유)

Router:

DB 모델 ↔ 스키마 간 매핑 처리 담당

에러는 errors.py의 코드만 사용 (raise_error())

→ 즉, 스키마·모델 필드가 달라도 OK,
→ 라우터에서 매핑해주면 됨.


⚠ 에러 처리

모든 라우터는 errors.py의 표준 에러 사용

raise_error(ErrorCodes.EMAIL_ALREADY_EXISTS)


응답 형식 통일:

{
  "status": 409,
  "error": "EMAIL_ALREADY_EXISTS",
  "message": "이미 사용 중인 이메일입니다."
}


-----

⭐ IEUM – Kakao REST API Key 설정 가이드 (README용)
🔐 Kakao Directions API 사용 방식 안내

우리 IEUM 프로젝트는 Kakao Directions API(경로 탐색) 를 사용합니다.
API 호출량 제한 및 보안 문제 때문에 모든 팀원이 각자 본인의 REST API 키를 발급해서 사용해야 합니다.

아래 과정을 따라 자신의 Kakao REST API Key를 설정하세요.

1) Kakao Developers 회원가입 및 로그인

🔗 https://developers.kakao.com/

카카오 계정으로 로그인합니다.

2) 새 애플리케이션 생성

좌측 메뉴 → 내 애플리케이션 → 애플리케이션 추가하기

이름은 자유롭게 입력
예: IEUM-개발용-홍길동

애플리케이션이 생성되면
REST API 키를 확인할 수 있습니다.

3) REST API 키 발급/확인

경로:
내 애플리케이션 → (내 앱 선택) → 앱 설정 → 일반 → 앱 키

여기서 REST API 키 값을 복사합니다.

4) .env 파일 생성 (프로젝트 루트)

프로젝트 루트에 .env 파일을 만들고 아래처럼 입력하세요:

KAKAO_REST_API_KEY=여기에_본인_키_입력
MONGO_URI=mongodb://...
JWT_SECRET=임의문자열


⚠ .env.template 파일을 참고해 동일 구조로 만들어주세요.
⚠ .env는 절대 git에 올라가지 않습니다.
⚠ 키는 각자 본인 것만 입력하면 됩니다.

5) FastAPI 서버 실행
docker-compose up --build


또는 로컬 개발 환경이라면:

uvicorn api.main:app --reload


정상 실행되면 Swagger UI에서 /route/ API 테스트가 가능합니다.

6) 주의 사항 (보안)

🔒 Kakao REST API Key는 절대 공유하지 마세요.
🔒 깃허브에 절대 올리지 마세요.
🔒 카카오 개발자센터에서 "앱 키 사용 이력"을 확인할 수 있으니
이상 사용량이 보이면 즉시 재발급하세요.

-----


🚧 D 단계 (안전 점수 엔진) — Skeleton Setup

본 단계에서는 E 단계의 /routes/safe API 구현을 위한 기반 엔진만 제공합니다.
아직 실제 안전 점수 계산(Hazard Join) 로직은 포함되지 않았으며,
Swagger에도 디버그 엔드포인트만 노출된 상태입니다.

📁 추가된 파일 (3개)
api/
 ├─ schemas/
 │    └── safe_route_schema.py      ← Safety Route Response 스키마 뼈대
 │
 ├─ services/
 │    └── safe_route_service.py     ← 안전 점수 계산 엔진 뼈대
 │
 └─ routers/
      └── safe_route.py             ← D 단계 뼈대 라우터(GET /routes/safe/debug)

📌 Swagger 노출 상태 (D 단계)

현재 Swagger 문서에는 아래 엔드포인트 1개만 표시됩니다:

GET /routes/safe/debug


해당 엔드포인트는 D 단계의 뼈대가 정상적으로 연결되었는지 확인하기 위한 임시 테스트용 API입니다.

⚠️ 주의:
이 API는 E 단계에서 완성될 POST /routes/safe 로 교체되며,
D 단계가 완료되면 삭제될 예정입니다.

🧩 D 단계의 역할 (핵심 요약)

D 단계는 경로 후보(C단계) + Hazard 데이터(DB)를 결합하여
각 경로의 안전 점수를 계산하는 엔진을 구축하는 단계입니다.

아직 실제 계산 로직은 포함되지 않았으며, 아래 작업이 예정되어 있습니다:

경로 경유 포인트(path)의 hazard 근접도 계산

hazard severity/type 가중치 적용

위험도 합산 → safetyScore 산출

경로들 중 최적(bestRouteIndex) 반환

모든 로직은 safe_route_service.py 안의 TODO로 표시되어 있습니다.

🔧 main.py 변경 사항

/routes/safe/debug가 Swagger에 표시되도록 다음 라우터가 등록되었습니다:

from api.routers import safe_route
app.include_router(safe_route.router)

📝 E 단계에서 이어서 구현해야 할 내용

E 단계에서는 다음 기능을 실제 구현하게 됩니다:

POST /routes/safe API 생성

C 단계의 경로 후보 + D 단계의 엔진을 결합하여
“최종 안전 경로” 반환

hazard 기반 safetyScore 실제 계산

bestRouteIndex 계산

Request 스키마 정의

✔ 상태 요약
단계	내용	상태
C 단계	기본 경로 후보 /route	완료
D 단계	안전 점수 엔진 뼈대	완료 (현재 진행 중)
E 단계	/routes/safe 완성	다음 단계
F 단계	실시간 안내·턴바이턴	이후 단계
