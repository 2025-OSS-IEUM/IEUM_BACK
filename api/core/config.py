from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 기본 프로젝트 설정
    PROJECT_NAME: str = "IEUM Backend"
    VERSION: str = "1.0.0"

    # --- 환경 변수 (.env 파일에서 읽어옴) ---
    MONGO_URI: str
    SECRET_KEY: str
    
    # (FIXED) .env의 DB_NAME을 읽어오도록 선언
    DB_NAME: str 
    
    # (FIXED) .env의 ACCESS_TOKEN_EXPIRE_MINUTES를 읽어오도록 선언
    ACCESS_TOKEN_EXPIRE_MINUTES: int 

    # 카카오 API 키 .env에서 읽어옴
    KAKAO_API_KEY: str

    class Config:
        env_file = ".env"  # 환경 변수 파일 지정
        env_file_encoding = "utf-8"


# settings 객체를 전역으로 사용
settings = Settings()

print("[api/core/config.py] Settings 로드 완료.")