from pydantic import BaseModel

class AccountCreate(BaseModel):
    user_id: int
    name: str
    type: str
    currency: str


class AccountUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    currency: str | None = None


class AccountResponse(BaseModel):
    id: int
    user_id: int
    name: str
    type: str
    currency: str

    model_config = {"from_attributes": True}