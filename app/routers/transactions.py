from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionUpdate
from app.models.user import User
from app.database import get_db
from app.services import transaction_service
from app.services.auth_service import get_current_user



router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create(data: TransactionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return transaction_service.create_transaction(db, current_user.id, data)

@router.get("/", response_model=list[TransactionResponse])
def get_all(account_id: int | None = None,
            category_id: int | None = None,
            transaction_type: str | None = None,
            skip: int = 0,
            limit: int = 20,
            current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db)):
    return transaction_service.get_transactions(db, current_user.id, account_id, category_id, transaction_type, skip, limit)


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_one(transaction_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return transaction_service.get_transaction(db, current_user.id, transaction_id)

@router.put("/{transaction_id}", response_model=TransactionResponse)
def update(transaction_id: int, data: TransactionUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return transaction_service.update_transaction(db, current_user.id, transaction_id, data)

@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(transaction_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    transaction_service.delete_transaction(db, current_user.id, transaction_id)