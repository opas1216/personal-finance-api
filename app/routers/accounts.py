from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.account import AccountCreate, AccountUpdate, AccountResponse
from app.services import account_service

router = APIRouter(prefix="/accounts", tags=["accounts"])

@router.post("/", response_model=AccountResponse)
def create(data: AccountCreate, db: Session = Depends(get_db)):
    return account_service.create_account(db, data)


@router.get("/<user_id: int>")
def get_all(user_id: int, db: Session = Depends(get_db)):
    return account_service.get_accounts(db, user_id)

def get_one():
