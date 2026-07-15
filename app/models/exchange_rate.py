from sqlalchemy import Column, String, Integer, Numeric, Float, DateTime, Date, UniqueConstraint, func
from app.database import Base

class ExchangeRate(Base):
    __tablename__ = "exchange_rates"
    id              = Column(Integer, primary_key=True)
    base_currency   = Column(String(3), nullable=False)
    target_currency = Column(String(3), nullable=False)
    rate            = Column(Numeric(18, 8), nullable=False)
    as_of_date      = Column(Date, nullable=False)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("base_currency", "target_currency", "as_of_date", name="uq_exchange_rate_pair_date"),
    )

