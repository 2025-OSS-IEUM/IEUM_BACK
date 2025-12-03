from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 기본 프로젝트 설정
    PROJECT_NAME: str = "IEUM Backend"
    VERSION: str = "1.0.0"

    # --- 환경 변수 (.env 파일에서 읽어옴) ---
    MONGO_URI: str
    SECRET_KEY: str
    DB_NAME: str 
    ACCESS_TOKEN_EXPIRE_MINUTES: int 
    KAKAO_API_KEY: str

    # 캐시(Redis)
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: str | None = None

    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

print("[api/core/config.py] Settings 로드 완료.")


# --------------------------------------------
# 🌟 Hazard weights (변경 없음)
# --------------------------------------------
HAZARD_WEIGHTS = {
    "sidewalk_damage": 1.2,
    "construction": 1.0,
    "missing_crosswalk": 1.5,
    "no_tactile": 0.8,
    "etc": 0.5
}


# --------------------------------------------
# 🌟 severity: 숫자 기반 가중치 맵 (1~5 입력)
# --------------------------------------------
SEVERITY_WEIGHTS = {
    1: 1.0,
    2: 1.0,
    3: 1.5,
    4: 2.0,
    5: 2.0,
}

