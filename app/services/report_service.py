from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from app.models.transaction import Transaction
from app.models.category import Category
from app.schemas.report import MonthlySummary, CategorySummary



def get_monthly_summary(db: Session, user_id: int, year: int, month: int) -> MonthlySummary:
    def sum_by_type(transaction_type: str) -> Decimal:
        result = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == transaction_type,
            func.extract('year', Transaction.transaction_date) == year,
            func.extract('month', Transaction.transaction_date) == month
        ).scalar()

        return result or Decimal("0")

    total_income = sum_by_type("income")
    total_expense = sum_by_type("expense")

    return MonthlySummary(
        year=year,
        month=month,
        total_income=total_income,
        total_expense=total_expense,
        net=total_income - total_expense,
    )


def get_category_summary(db: Session, user_id: int, year: int, month: int) -> list[CategorySummary]:
    results = db.query(Category.name,
             Transaction.transaction_type,
             func.sum(Transaction.amount).label("total")
             ).select_from(Transaction).join(Category, Transaction.category_id == Category.id).filter(
        Transaction.user_id == user_id,
        func.extract('year', Transaction.transaction_date) == year,
        func.extract('month', Transaction.transaction_date) == month
    ).group_by(Category.name, Transaction.transaction_type).all()

    return [
        CategorySummary(
            category_name=row.name,
            transaction_type=row.transaction_type,
            total=row.total
        ) for row in results
    ]



