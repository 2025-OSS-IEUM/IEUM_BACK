# app/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # .env 파일이 없으면 이 기본값을 사용합니다.
    DATABASE_URL: str = "sqlite:///./temp_fastapi.db" # 임시 DB
    API_V1_STR: str = "/api" # 모든 API 앞에 붙일 경로

    class Config:
        env_file = ".env" # .env 파일을 읽어들임 (A-3 담당)

# settings 객체를 생성하여 다른 파일에서 import하여 사용
settings = Settings()