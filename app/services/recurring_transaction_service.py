from sqlalchemy.orm import Session
from app.schemas.recurring_transaction import RecurringTransactionCreate, RecurringTransactionResponse, RecurringTransactionUpdate
from app.models.recurring_transactions import RecurringTransaction
from app.exceptions import NotFoundException



def create_recurring_transaction(db: Session, user_id: int, data: RecurringTransactionCreate) -> RecurringTransaction:
    # Create a new recurring transaction
    recurring_transaction = RecurringTransaction(**data.model_dump(), user_id=user_id)

    db.add(recurring_transaction)
    db.commit()
    db.refresh(recurring_transaction)

    return recurring_transaction


def get_one(db: Session, user_id: int, recurring_transaction_id: int) -> RecurringTransaction:
    # Get a single recurring transaction by ID
    recurring_transaction = db.query(RecurringTransaction).filter(RecurringTransaction.user_id == user_id, RecurringTransaction.id == recurring_transaction_id).first()

    if not recurring_transaction:
        raise NotFoundException("Recurring transaction not found")

    return recurring_transaction

def get_all(db: Session, user_id: int) -> list[RecurringTransaction]:
    # Get all recurring transactions for a user
    recurring_transactions = db.query(RecurringTransaction).filter(RecurringTransaction.user_id == user_id).all()

    return recurring_transactions


def update_recurring_transaction(db: Session, user_id: int, recurring_transaction_id: int, data: RecurringTransactionUpdate):
    recurring_transaction = db.query(RecurringTransaction).filter(RecurringTransaction.user_id == user_id, RecurringTransaction.id == recurring_transaction_id).first()


def delete_recurring_transaction:
