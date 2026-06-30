from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.transaction import Transaction
from app.models.account import Account
from app.models.category import Category
from app.schemas.transaction import TransactionCreate, TransactionUpdate
from app.exceptions import NotFoundException




def create_transaction(db: Session, user_id: int, data: TransactionCreate) -> Transaction:
    # validate whether the account exists and belongs to the user
    account = db.query(Account).filter(Account.id == data.account_id, Account.user_id == user_id).first()
    if not account:
        raise NotFoundException("Account not found")

    # validate whether the category exists and belongs to the user
    if data.category_id:
        category = db.query(Category).filter(Category.id == data.category_id, Category.user_id == user_id).first()
        if not category:
            raise NotFoundException("Category not found")


    transaction = Transaction(**data.model_dump(), user_id=user_id)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def get_transaction(db: Session, user_id: int, transaction_id: int) -> Transaction:
    transaction = db.query(Transaction).filter(Transaction.user_id == user_id, Transaction.id == transaction_id).first()

    if not transaction:
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
        raise NotFoundException("Transaction not found")

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
    transaction = get_transaction(db, user_id, transaction_id)

    if data.account_id:
        # 確認輸入的更新資料，account_id 是否存在且屬於該使用者
        account = db.query(Account).filter(Account.id == data.account_id, Account.user_id == user_id).first()
        if not account:
            raise NotFoundException("Account not found")

    if data.category_id:
        category = db.query(Category).filter(Category.id == data.category_id, Category.user_id == user_id).first()
        if not category:
            raise NotFoundException("Category not found")

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(transaction, key, value)

    db.commit()
    db.refresh(transaction)

    return transaction


def delete_transaction(db: Session, user_id: int, transaction_id: int):
    query = db.query(Transaction).filter(Transaction.user_id == user_id)

    transaction = query.filter(Transaction.id == transaction_id).first()

    if not transaction:
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
        raise NotFoundException("Transaction not found")

    db.delete(transaction)
    db.commit()
