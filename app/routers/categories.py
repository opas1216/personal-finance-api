from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services import category_service

router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("/", response_model=CategoryResponse)
def create(data: CategoryCreate, db: Session = Depends(get_db)):
    return category_service.create_category(db, data)


@router.get("/<user_id: int>")
def get_all(user_id: int, db: Session = Depends(get_db)):
    return category_service.get_categories(db, user_id)

def get_one():
