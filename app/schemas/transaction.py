from pydantic import BaseModel
from datetime import date
from decimal import Decimal
from typing import Literal


class TransactionCreate(BaseModel):
    account_id: int
    category_id: int | None = None
    amount: Decimal
    transaction_type: Literal["income", "expense"]   # income or expense
    transaction_date: date
    description: str | None = None


class TransactionUpdate(BaseModel):
    account_id: int | None = None
    category_id: int | None = None
    amount: Decimal | None = None
    transaction_type: Literal["income", "expense"] | None = None  # income or expense
    transaction_date: date | None = None
    description: str | None = None

class TransactionResponse(BaseModel):
    id: int
    user_id: int
    account_id: int
    category_id: int | None = None
    amount: Decimal
    transaction_type: str  # income or expense
    transaction_date: date
    description: str | None = None

    model_config = {"from_attributes": True}