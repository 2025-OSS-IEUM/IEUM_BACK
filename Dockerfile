# Dockerfile
# 1. 베이스 이미지 (Python 3.11 슬림 버전)
FROM python:3.11-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. (중요) api 폴더 안의 requirements.txt 파일을 먼저 복사
#    - 이렇게 분리하면, requirements.txt가 변경될 때만 pip install을 다시 실행 (도커 캐시 활용)
COPY ./api/requirements.txt .

# 4. 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 5. api 폴더의 모든 소스 코드를 컨테이너 /app 디렉토리로 복사
COPY ./api /app

# 6. FastAPI가 실행될 8000번 포트 노출
EXPOSE 8000

# (참고) 기본 실행 명령어는 docker-compose.yml의 command가 덮어씁니다.
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]