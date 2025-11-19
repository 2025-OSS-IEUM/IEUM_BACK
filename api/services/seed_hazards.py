# api/services/seed_hazards.py

from db.database import reports_collection
from motor.motor_asyncio import AsyncIOMotorCollection
import asyncio
from datetime import datetime


SEED_HAZARDS = [
    {
        "type": "construction",
        "severity": 3,
        "status": "approved",   # ⭐ 추가됨
        "location": {
            "type": "Point",
            "coordinates": [126.988205, 37.551229]
        },
        "createdAt": datetime.utcnow(),
    },
    {
        "type": "accident",
        "severity": 4,
        "status": "approved",
        "location": {
            "type": "Point",
            "coordinates": [126.990441, 37.552801]
        },
        "createdAt": datetime.utcnow(),
    },
    {
        "type": "crowd",
        "severity": 2,
        "status": "approved",
        "location": {
            "type": "Point",
            "coordinates": [126.993311, 37.553920]
        },
        "createdAt": datetime.utcnow(),
    },
    {
        "type": "dark_area",
        "severity": 5,
        "status": "approved",
        "location": {
            "type": "Point",
            "coordinates": [126.987002, 37.550021]
        },
        "createdAt": datetime.utcnow(),
    },
    {
        "type": "uneven_surface",
        "severity": 3,
        "status": "approved",
        "location": {
            "type": "Point",
            "coordinates": [126.989450, 37.551112]
        },
        "createdAt": datetime.utcnow(),
    },
    {
        "type": "construction",
        "severity": 1,
        "status": "approved",
        "location": {
            "type": "Point",
            "coordinates": [126.992780, 37.553400]
        },
        "createdAt": datetime.utcnow(),
    },
    {
        "type": "crowd",
        "severity": 4,
        "status": "approved",
        "location": {
            "type": "Point",
            "coordinates": [127.0006307, 37.5512743]
        },
        "createdAt": datetime.utcnow(),
    },
    {
        "type": "accident",
        "severity": 2,
        "status": "approved",
        "location": {
            "type": "Point",
            "coordinates": [127.0002750, 37.5516407]
        },
        "createdAt": datetime.utcnow(),
    },
    {
        "type": "dark_area",
        "severity": 5,
        "status": "approved",
        "location": {
            "type": "Point",
            "coordinates": [126.998800, 37.550900]
        },
        "createdAt": datetime.utcnow(),
    },
    {
        "type": "uneven_surface",
        "severity": 1,
        "status": "approved",
        "location": {
            "type": "Point",
            "coordinates": [126.999321, 37.551450]
        },
        "createdAt": datetime.utcnow(),
    }
]


async def seed_hazard_data(collection: AsyncIOMotorCollection):
    print("⚠️ Creating 2dsphere index...")
    await collection.create_index([("location", "2dsphere")])

    print("⚠️ Removing old hazard data...")
    await collection.delete_many({})

    print("⚠️ Inserting new hazard seed data...")
    await collection.insert_many(SEED_HAZARDS)

    print("✅ Hazard seed data inserted successfully!")


if __name__ == "__main__":
    async def main():
        # reports_collection이 맞음 (hazard_reports)
        await seed_hazard_data(reports_collection)

    asyncio.run(main())
