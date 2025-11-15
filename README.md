# 이음(I-EUM)

2025 오픈소스SW프로그래밍 - 시각장애인을 위한 안전 보행 지도

---

## 💡 프로젝트 개요

단순한 거리·시간 기준의 경로 안내가 아닌,  
**계단·급경사·공사 구간·혼잡 행사 장소 등을 회피하고**  
**가로등, 안전도, 교통 정보를 종합적으로 고려한 안전 경로**를 안내합니다.

또한, 화면을 직접 보지 않아도 사용할 수 있도록  
**음성 안내(Voice Guide)** 및 **보이스오버 접근성(VoiceOver Accessibility)** 기능을 지원합니다.

---

## 🚨 서비스 필요성

| 기존 지도 앱의 한계 | SafeRoute의 해결 방식 |
|------------------|---------------------|
| 최단거리 위주 안내 → 위험 구간 미반영 | 안전요소 기반 경로 탐색 (계단/공사/혼잡 회피) |
| 불필요한 음성 정보 과다 | 핵심 정보만 간결하게 제공 |
| 휴무일/시설 정보 부족 | 병원·약국 휴무일 및 운영정보 제공 |
| 접근성 부족 | VoiceOver 및 음성 제어 완전 지원 |

> 이동권은 누구에게나 **보장받아야 할 권리**입니다.  
> 이음은 시각장애인의 **자유롭고 안전한 이동**을 목표로 합니다.

---

## 🗺️ 활용 공공데이터

| 출처 | 데이터명 | 활용 목적 |
|------|-----------|------------|
| 대전광역시 | 도로안전시설물 설치현황 | 점자블록·보행시설 반영 |
| 대전광역시 | 가로등 현황 | 야간 안전도 평가 |
| 대전광역시 | 도로시설물 현황(점형, 기타) | 장애물 회피 |
| 대전시 OpenAPI | 공사 데이터 | 공사구간 회피 |
| 대전시 OpenAPI | 행사 데이터 | 혼잡 지역 회피 |
| 대전시 OpenAPI | 실시간 교통정보 | 교통 신호·혼잡 반영 |
| 대전시 | 병원·약국 휴무일 데이터 | 목적지 영업 여부 확인 |
| 사용자 입력 | 위험 요소 제보 (크라우드소싱) | 실시간 위험 지역 업데이트 |

---

## ⚙️ 주요 기능

### 🧭 1. 안전 경로 탐색
- 최단 거리/시간보다 **안전 경로 우선 탐색**
- 계단, 급경사, 공사 구간 자동 회피
- 가로등 밀도 기반 야간 안전도 반영

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
- 목적지 **운영시간·휴무일 안내**
- 사용자 **위험 요소 제보 시스템**
- **도착지 리포트** 제공 (거리, 소요시간, 위험도 등)

## 📁 환경 변수 설정
   `.env.example` 파일을 참고하여 `.env` 파일을 생성하세요:
   ```bash
   cp .env.example .env
   .env 파일을 열고 실제 값을 채워 넣으세요:
---

## 🧩 기술 스택

| 분야 | 기술 |
|------|------|
| **Backend** | Python · Django / Flask |
| **Frontend** | React Native |
| **Database** | MySQL / SQLite |
| **Infra** | AWS EC2, S3 |
| **Data Source** | 공공데이터포털 (대전시 OpenAPI) |
| **Accessibility** | VoiceOver / TTS / Screen Reader API |

---

## 👥 팀 구성

| 역할 | 이름 | 주요 담당 |
|------|------|------------|
| 기획/PM (팀장) | **강윤서** | 전체 기획 · 데이터 연계 설계 · 발표 |
| 백엔드 | **이호민**, **송주환** | 공공데이터 수집/정제 · 경로 탐색 알고리즘 서버 구현 |
| 프론트엔드 | **우은식**, **강윤서** | UI 구현 · 보이스오버/음성 안내 연동 |
| 데이터/AI | **김정우** | 위험요소 탐지 알고리즘 · 사용자 제보 데이터 정제 |

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

📦 폴더 구조 (최종판)
IEUM_BACK/
 ├── api/
 │    ├── main.py
 │    ├── routers/
 │    ├── schemas/
 │    ├── db/
 │    ├── services/
 ├── Dockerfile
 ├── docker-compose.yml
 ├── requirements.txt
 └── .env   (⚠️ git에 포함 ❌)