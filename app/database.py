# 1. 讀取 DATABASE_URL — 從 .env 用 python-dotenv 載入
# 2. 建立 engine — SQLAlchemy 用來連接資料庫的核心物件
# 3. 建立 SessionLocal 和 Base — SessionLocal 是每個 request 的 DB session 工廠；Base 是之後所有 ORM model 繼承用的

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
      yield db
    finally:
      db.close()