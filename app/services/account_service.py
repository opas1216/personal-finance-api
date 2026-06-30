from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.account import Account
from app.schemas.account import AccountCreate, AccountUpdate
from app.exceptions import NotFoundException


def create_account(db: Session, data: AccountCreate) -> Account:
    # 1. 把 schema 轉成 model
    account = Account(**data.model_dump())

    # 2. db.add() → db.commit() → db.refresh()
    db.add(account)
    db.commit()
    db.refresh(account)

    # 3. return account
    return account


def get_account(db: Session, account_id: int) -> Account:
    """
        從DB抓出指定的account
    """
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        raise NotFoundException("Account not found")
    return account


def get_accounts(db: Session, user_id: int) -> list[Account]:
    return db.query(Account).filter(Account.user_id == user_id).all()


def update_account(db: Session, account_id: int, data: AccountUpdate) -> Account:
    account = get_account(db, account_id)

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(account, key, value)

    db.commit()
    db.refresh(account)
    return account


def delete_account(db: Session, account_id: int) -> None:
    account = get_account(db, account_id)
    db.delete(account)
    db.commit()