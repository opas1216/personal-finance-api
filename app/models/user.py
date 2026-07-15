from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base



# 登入身分
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    base_currency = Column(String(3), nullable=False, server_default="TWD")  # 新增 base_currency 欄位，預設為 TWD

