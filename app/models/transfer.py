from sqlalchemy import Column, ForeignKey, Integer, String, Numeric, Date, DateTime, func
from app.database import Base


class Transfer(Base):
    __tablename__ = 'transfers'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    source_account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    destination_account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    source_amount = Column(Numeric(10, 2), nullable=False)
    destination_amount = Column(Numeric(10, 2), nullable=False)
    transfer_date = Column(Date, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

