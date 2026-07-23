from pydantic import BaseModel, field_validator
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

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("amount must be greater than 0")
        return v


class TransactionUpdate(BaseModel):
    account_id: int | None = None
    category_id: int | None = None
    amount: Decimal | None = None
    transaction_type: Literal["income", "expense"] | None = None  # income or expense
    transaction_date: date | None = None
    description: str | None = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("amount must be greater than 0")
        return v

class TransactionResponse(BaseModel):
    id: int
    user_id: int
    account_id: int
    category_id: int | None = None
    amount: Decimal
    transaction_type: str  # income or expense
    transaction_date: date
    description: str | None = None
    exchange_rate_to_base: Decimal
    base_currency_amount: Decimal

    model_config = {"from_attributes": True}