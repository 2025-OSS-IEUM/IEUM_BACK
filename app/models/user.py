# app/models/user.py

from sqlalchemy import Column, Integer, String
from app.db.session import Base # 2단계에서 만든 Base 클래스를 가져옵니다.

# [수업 자료 활용 1: 파이썬 데이터 모델 (02.들어가며.pdf)]
#
# User 클래스는 DB 테이블 'users'에 매핑되는 '데이터 모델'입니다.
#
# 수업 자료의 'FrenchDeck' 클래스나 'Vector' 클래스(02.들어가며.pdf)처럼,
# User 객체도 고유한 데이터(id, email 등)와 동작(__repr__)을 갖습니다.
#
# 또한 'namedtuple'이 데이터를 담는 '레코드' 역할을 하듯(03.데이터구조체-시퀀스.pdf),
# 이 User 클래스도 사용자 정보를 담는 '레코드' 역할을 합니다.
class User(Base):
    __tablename__ = "users" # DB에 생성될 테이블 이름

    # 분담표(A-1)에서 요청한 필드들을 정의합니다.
    id = Column(Integer, primary_key=True, index=True) # 고유 ID
    email = Column(String, unique=True, index=True, nullable=False) # 이메일 (로그인 시 사용)
    
    # 'password_hash', 'level', 'exp'
    password_hash = Column(String, nullable=False) # A-3 담당자가 채울 해시된 비밀번호
    level = Column(Integer, default=1)
    exp = Column(Integer, default=0)
    
    # (추가로 필요한 사용자 이름(username) 등도 여기에 Column으로 추가할 수 있습니다)


    # [수업 자료 활용 2: 특별 메서드 __repr__ (02.들어가며.pdf)]
    #
    # __repr__은 파이썬의 '특별 메서드'(Special Method)입니다 (02.들어가며.pdf).
    # 'Vector' 클래스나 'Test' 클래스(02.들어가며.pdf)에서
    # 객체를 사람이 읽기 쉬운 문자열로 표현하기 위해 __repr__을 사용했습니다.
    #
    # 우리도 User 객체를 print() 하거나 디버깅할 때 객체 정보를 명확히
    # 볼 수 있도록 __repr__ 특별 메서드를 구현합니다.
    def __repr__(self):
        return f"<User(id={self.id!r}, email={self.email!r}, level={self.level})>"