# scripts/ensure_indexes.py
import asyncio
from app.db.init_indexes import ensure_indexes

if __name__ == "__main__":
    print("Ensuring Mongo indexes for 'hazard_reports' ...")
    print(asyncio.run(ensure_indexes()))
#단독 실행(서버 없이)
