from pydantic import BaseModel, field_validator
from decimal import Decimal
from datetime import datetime, date
from typing import Literal


class RecurringTransactionCreate(BaseModel):
    account_id: int
    category_id: int | None = None
    amount: Decimal
    transaction_type: Literal["income", "expense"]  # income or expense
    frequency: str
    interval: int
    description: str | None = None
    start_date: date
    end_date: date | None = None

    @field_validator("start_date")
    @classmethod
    def start_date_must_not_be_past(cls, v):
        if v < date.today():
            raise ValueError("start_date must not be in the past")
        return v



class RecurringTransactionResponse(BaseModel):
    id: int
    user_id: int
    account_id: int
    category_id: int | None = None #實際上這裡的預設值會被DB的資料給覆蓋，根本不會用到，會這樣寫只是因為Pydantic 的慣例寫法（宣告成 Optional 型別時,習慣上都會搭配給一個預設值）
    amount: Decimal
    transaction_type: str
    frequency: str
    interval: int
    description: str | None = None
    start_date: date
    next_run_date: date
    end_date: date | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class RecurringTransactionUpdate(BaseModel):
    account_id: int | None = None
    category_id: int | None = None
    amount: Decimal | None = None
    transaction_type: Literal["income", "expense"] | None = None  # income or expense
    frequency: str | None = None
    interval: int | None = None
    description: str | None = None
    end_date: date | None = None
    is_active: bool | None = None

