from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate, UserResponse, Token, UserLogin
from app.database import get_db
from app.services import auth_service
from app.services.auth_service import get_current_user
from app.models.user import User
from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    return auth_service.register(db, data)

# 使用UserLogin schema的方式
# @router.post("/login", response_model=Token)
# def login(data: UserLogin, db: Session = Depends(get_db)) -> Token:
#     return auth_service.login(db, data.email, data.password)


# 使用OAuth2PasswordRequestForm的方式，這是FastAPI內建的表單格式，適合與前端的OAuth2密碼模式配合使用
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Token:
    return auth_service.login(db, form_data.username, form_data.password)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return current_user
