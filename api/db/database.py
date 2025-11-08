# 파일의 역할 MongoDB 연결 설정 + users 컬렉션 핸들 준비

from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)
db = client["ieum_db"]
users_collection = db["users"]


