from pydantic import BaseModel


class CategoryCreate(BaseModel):
    # introduce the JWT token to get the user_id from the token instead of passing it in the request body
    # user_id: int
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

