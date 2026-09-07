from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, Date, DateTime, func
from app.database import Base

class RecurringTransaction(Base):
    __tablename__ = "recurring_transactions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    amount = Column(Numeric(10, 2), nullable=False)
    transaction_type = Column(String, nullable=False)
    frequency = Column(String, nullable=False)  # e.g., daily, weekly, monthly
    interval = Column(Integer, nullable=False)  # e.g., 1, 2, 10, etc
    description = Column(String, nullable=True)
    start_date = Column(Date, nullable=False)
    next_run_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

