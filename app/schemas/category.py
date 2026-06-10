from pydantic import BaseModel


class CategoryCreate(BaseModel):
    user_id: int
    name: str
    type: str

class CategoryUpdate(BaseModel):
    name: str | None = None
    type: str | None = None

class CategoryResponse(BaseModel):
    id: int
    user_id: int
    name: str
    type: str

    model_config = {'from_attributes': True}

