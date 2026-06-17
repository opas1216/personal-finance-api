from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, UserResponse
from app.database import get_db
from app.services import auth_service

router = APIRouter(prefx="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    return auth_service.register(db, data)



@router.post("/login")
def login()
