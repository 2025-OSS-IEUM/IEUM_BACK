from pydantic import BaseSettings

class Settings(BaseSettings):
    # 기본 프로젝트 설정
    PROJECT_NAME: str = "IEUM Backend"
    VERSION: str = "1.0.0"

    # 환경 변수
    MONGO_URI: str
    SECRET_KEY: str

    class Config:
        env_file = ".env"  # 환경 변수 파일 지정
        env_file_encoding = "utf-8"


# settings 객체를 전역으로 사용
settings = Settings()
