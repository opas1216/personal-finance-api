from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services import category_service
from app.models.user import User
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("/", response_model=CategoryResponse, status_code=201)
def create(data: CategoryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return category_service.create_category(db, current_user.id, data)


@router.get("/", response_model=list[CategoryResponse])
def get_all(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return category_service.get_categories(db, current_user.id)

@router.get("/{category_id}", response_model=CategoryResponse)
def get_one(category_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return category_service.get_category(db, category_id, current_user.id)


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, data: CategoryUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return category_service.update_category(db, category_id, current_user.id, data)

@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    category_service.delete_category(db, category_id, current_user.id)
