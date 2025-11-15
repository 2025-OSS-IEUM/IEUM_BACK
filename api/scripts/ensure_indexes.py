import asyncio
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING

# 1. (FIXED) 'app.db.mongo' (삭제할 파일) 대신 'api.db.database' (남기기로 한 파일)에서
#    db 객체를 직접 import 합니다.
from api.db.database import db 

# (참고: 'app.utils.errors'도 'app' 폴더와 함께 삭제될 것이므로,
#  'err' 함수 대신 기본 print/raise를 사용하도록 변경했습니다.)

COLL = "hazard_reports"

# Mongo 컬렉션 레벨 검증 (Pydantic 스키마와 일치)
JSON_SCHEMA = {
    "bsonType": "object",
    "required": ["type", "description", "location", "severity", "status"],
    "properties": {
        "type":        {"enum": ["sidewalk_damage", "construction", "missing_crosswalk", "no_tactile", "etc"]},
        "description": {"bsonType": "string"},
        "location":    {
            "bsonType": "object",
            "required": ["type", "coordinates"],
            "properties": {
                "type": {"enum": ["Point"]},
                "coordinates": {
                    "bsonType": "array",
                    "items": [{"bsonType": "double"}, {"bsonType": "double"}],
                    "minItems": 2,
                    "maxItems": 2
                }
            }
        },
        "photoUrls": {"bsonType": ["array"]},
        "detectedAt": {"bsonType": ["date", "null"]},
        "severity": {"enum": ["low", "medium", "high"]},
        "status":   {"enum": ["pending_review", "approved", "resolved"]}
    }
}

async def ensure_indexes(db_conn: AsyncIOMotorDatabase | None = None) -> dict:
    """
    (B-1) hazard_reports 컬렉션이 없으면 생성하고,
    2dsphere(location), 시간/상태 보조 인덱스를 보장.
    """
    try:
        # 2. (FIXED) get_db() 함수를 호출할 필요 없이, import한 db 객체를 사용합니다.
        db_to_use = db_conn or db

        # 컬렉션 생성(기 존재 시 pass)
        if COLL not in await db_to_use.list_collection_names():
            await db_to_use.create_collection(
                COLL,
                validator={"$jsonSchema": JSON_SCHEMA},
                validationLevel="moderate",
            )
            print(f"MongoDB: 컬렉션 '{COLL}' 생성 및 스키마 적용 완료.")

        coll = db_to_use[COLL]

        # 공간 인덱스 (GIST / 2dsphere)
        await coll.create_index([("location", "2dsphere")], name="idx_location_2dsphere")

        # 조회 보조 인덱스
        await coll.create_index([("detectedAt", ASCENDING)], name="idx_detectedAt")
        await coll.create_index([("status", ASCENDING)], name="idx_status")

        result = {"message": "indexes ensured", "collection": COLL}
        print(f"MongoDB: {result}")
        return result

    except Exception as e:
        # 3. (FIXED) 'app.utils.errors' 의존성 제거
        print(f"MongoDB 인덱스 생성 중 오류 발생: {e}")
        raise e

if __name__ == "__main__":
    """
    이 스크립트를 단독으로 실행할 때 (예: python -m scripts.ensure_indexes)
    MongoDB에 연결하여 인덱스를 생성합니다.
    """
    print("MongoDB 인덱스 생성을 시작합니다...")
    asyncio.run(ensure_indexes())
    print("MongoDB 인덱스 생성 완료.")