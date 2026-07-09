from sqlalchemy import Column, String, Integer, ForeignKey

from app.database import Base

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)   # 自定義名稱，外送/聚會/外食/減肥餐等等這種被大領域包裹的小領域自定義名稱
    type = Column(String, nullable=False) # 食衣住行等這種大領域分類
