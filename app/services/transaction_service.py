from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate



def create_transaction(db: Session, user_id: int, data: TransactionCreate) -> Transaction:
    transaction = Transaction(**data.model_dump(), user_id=user_id)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def get_transaction(db: Session, user_id: int, transaction_id: int) -> Transaction:
    transaction = db.query(Transaction).filter(Transaction.user_id == user_id, Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    return transaction


def get_transactions(db: Session, user_id: int, account_id: int | None = None, category_id: int | None = None,
                     transaction_type: str | None = None, skip: int = 0, limit: int = 20) -> list[Transaction]:
    query = db.query(Transaction).filter(Transaction.user_id == user_id)

    if account_id:
        query = query.filter(Transaction.account_id == account_id)

    if category_id:
        query = query.filter(Transaction.category_id == category_id)

    if transaction_type:
        query = query.filter(Transaction.transaction_type == transaction_type)

    transactions = query.offset(skip).limit(limit).all()
    return transactions



def update_transaction(db: Session, user_id: int, transaction_id: int, data: TransactionUpdate):
    query = db.query(Transaction).filter(Transaction.user_id == user_id)

    transaction = query.filter(Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(transaction, key, value)

    db.commit()
    db.refresh(transaction)

    return transaction


def delete_transaction(db: Session, user_id: int, transaction_id: int):
    query = db.query(Transaction).filter(Transaction.user_id == user_id)

    transaction = query.filter(Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    db.delete(transaction)
    db.commit()
