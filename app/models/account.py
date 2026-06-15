from sqlalchemy import Column, Integer, String, ForeignKey
from app.database import Base

# 這裡定義Table的結構，對應到資料庫中的accounts table
class Account(Base):
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    currency = Column(String, nullable=False)