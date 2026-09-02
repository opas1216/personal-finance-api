from pydantic import BaseModel, field_validator
from datetime import date, datetime
from decimal import Decimal
from typing import Literal



class TransferCreate(BaseModel):
    source_account_id: int
    destination_account_id: int
    source_amount: Decimal
    transfer_date: date
    description: str| None = None

    @field_validator("source_amount")
    @classmethod
    def source_amount_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("source_amount must be greater than 0")
        return v


class TransferResponse(BaseModel):
    id: int
    user_id: int
    source_account_id: int
    destination_account_id: int
    source_amount: Decimal
    destination_amount: Decimal
    transfer_date: date
    description: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
