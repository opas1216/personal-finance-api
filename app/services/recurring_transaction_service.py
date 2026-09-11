from sqlalchemy.orm import Session

from app.models import Category
from app.models import Account
from app.models import RecurringTransaction
from app.schemas.recurring_transaction import RecurringTransactionCreate, RecurringTransactionResponse, RecurringTransactionUpdate
from app.exceptions import NotFoundException
from datetime import date, datetime, timedelta


def calculate_next_run_date(start_date: date, frequency: str, interval: int):
    if frequency == "daily":
        return start_date + timedelta(days=interval)
    elif frequency == "weekly":
        return start_date + timedelta(weeks=interval)
    elif frequency == "monthly":
        month = start_date.month - 1 + interval #transfrom to 0-based.
        year = start_date.year + month // 12
        month = month % 12 + 1  # transform back to 1-based
        day = min(start_date.day, [31,
                                   29 if year % 4 == 0 and not year % 100 == 0 or year % 400 == 0 else 28,
                                   31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
        return date(year, month, day)
    elif frequency == "yearly":
        year = start_date.year + interval
        month = start_date.month
        day = min(start_date.day, [31,
                                   29 if year % 4 == 0 and not year % 100 == 0 or year % 400 == 0 else 28,
                                   31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
        return date(year, month, day)
    else:
        raise ValueError("Invalid frequency. Must be 'daily', 'weekly', or 'monthly'.")



def create_recurring_transaction(db: Session, user_id: int, data: RecurringTransactionCreate) -> RecurringTransaction:
    # calculate the next run date based on the start date, frequency, and interval
    next_run_date = calculate_next_run_date(data.start_date, data.frequency, data.interval)

    # Create a new recurring transaction
    account = db.query(Account).filter(Account.id == data.account_id, Account.user_id == user_id).first()
    if not account:
        raise NotFoundException("Account not found")

    if data.category_id:
        category = db.query(Category).filter(Category.id == data.category_id, Category.user_id == user_id).first()
        if not category:
            raise NotFoundException("Category not found")

    recurring_transaction = RecurringTransaction(**data.model_dump(), user_id=user_id, next_run_date=next_run_date)

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
    if not recurring_transaction:
        raise NotFoundException("Recurring transaction not found")

    if data.account_id:
        account = db.query(Account).filter(Account.id == data.account_id, Account.user_id == user_id).first()
        if not account:
            raise NotFoundException("Account not found")

    if data.category_id:
        category = db.query(Category).filter(Category.id == data.category_id, Category.user_id == user_id).first()
        if not category:
            raise NotFoundException("Category not found")

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(recurring_transaction, key, value)

    if data.frequency or data.interval:
        if data.start_date:
            start_date = data.start_date
        else:
            start_date = recurring_transaction.start_date
        next_run_date = calculate_next_run_date(recurring_transaction.start_date,
                                                data.frequency or recurring_transaction.frequency,
                                                data.interval or recurring_transaction.interval)
    else:
        if data.start_date:
            next_run_date = calculate_next_run_date(data.start_date,
                                                    recurring_transaction.frequency,
                                                    recurring_transaction.interval)


    db.commit()
    db.refresh(recurring_transaction)

    return recurring_transaction

def delete_recurring_transaction(db: Session, user_id: int, recurring_transaction_id: int):
    recurring_transaction = db.query(RecurringTransaction).filter(RecurringTransaction.id == recurring_transaction_id, RecurringTransaction.user_id == user_id).first()
    if not recurring_transaction:
        raise NotFoundException("Recurring transaction not found")

    setattr(recurring_transaction, "is_active", False)

    db.commit()
    db.refresh(recurring_transaction)

    return recurring_transaction



