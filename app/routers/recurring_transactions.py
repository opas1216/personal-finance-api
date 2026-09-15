from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.recurring_transaction import RecurringTransactionCreate, RecurringTransactionResponse, RecurringTransactionUpdate
from app.services.auth_service import get_current_user
from app.services import recurring_transaction_service


router = APIRouter(prefix="/recurring-transactions", tags=["recurring_transactions"])


@router.post("/", response_model=RecurringTransactionResponse, status_code=status.HTTP_201_CREATED)
def create(data: RecurringTransactionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return recurring_transaction_service.create_recurring_transaction(db, current_user.id, data)

@router.get("/", response_model=list[RecurringTransactionResponse])
def get_all(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return recurring_transaction_service.get_recurring_transactions(db, current_user.id)

@router.put("/{recurring_transaction_id}", response_model=RecurringTransactionResponse)
def update(data: RecurringTransactionUpdate, recurring_transaction_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return recurring_transaction_service.update_recurring_transaction(db, current_user.id, recurring_transaction_id, data)

@router.get("/{recurring_transaction_id}", response_model=RecurringTransactionResponse)
def get_one(recurring_transaction_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return recurring_transaction_service.get_recurring_transaction(db, current_user.id, recurring_transaction_id)

@router.delete("/{recurring_transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(recurring_transaction_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    recurring_transaction_service.delete_recurring_transaction(db, current_user.id, recurring_transaction_id)







