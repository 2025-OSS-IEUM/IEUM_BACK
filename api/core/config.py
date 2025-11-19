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

<<<<<<< HEAD
    # 캐시(Redis) 관련 설정
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    # 필요하면 비밀번호도
    REDIS_PASSWORD: str | None = None

    # 로그 관련 설정
    LOG_LEVEL: str = "INFO"

=======
>>>>>>> 0557621a7f2205829bcfec166f52a83453873b11
    class Config:
        env_file = ".env"  # 환경 변수 파일 지정
        env_file_encoding = "utf-8"


# settings 객체를 전역으로 사용
settings = Settings()

print("[api/core/config.py] Settings 로드 완료.")


HAZARD_WEIGHTS = {
    "sidewalk_damage": 1.2,
    "construction": 1.0,
    "missing_crosswalk": 1.5,
    "no_tactile": 0.8,
    "etc": 0.5
}

SEVERITY_WEIGHTS = {
    "low": 1.0,
    "medium": 1.5,
    "high": 2.0
}