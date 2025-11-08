# app/db/session.py

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base # (ORM)
from sqlalchemy.orm import sessionmaker
from app.core.config import settings # A-2에서 만든 config.py의 settings를 import

# 1. create_engine: 실제 DB와 연결(Connection Pool)
#    config.py의 DATABASE_URL을 사용합니다. (A-3 담당자가 .env에 채울 예정)
engine = create_engine(settings.DATABASE_URL)

# 2. sessionmaker: DB와 통신하기 위한 세션(Session)을 만드는 클래스
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Base: 모든 DB 모델(테이블)이 상속받을 부모 클래스
#    이 Base를 상속받아 User 같은 모델을 만듭니다.
Base = declarative_base()