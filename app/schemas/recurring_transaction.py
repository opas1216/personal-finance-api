from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime, date


class RecurringTransactionCreate(BaseModel):
    account_id: int
    category_id: int | None = None
    amount: Decimal
    transaction_type: str = "expense"
    frequency: str
    interval: int
    description: str | None = None
    start_date: date
    next_run_date: date
    end_date: date | None = None


