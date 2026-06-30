from pydantic import BaseModel
from decimal import Decimal

class MonthlySummary(BaseModel):
    year: int
    month: int
    total_income: Decimal   # 收入加總
    total_expense: Decimal  # 支出加總
    net: Decimal    # 收入 - 支出 = 淨額




class CategorySummary(BaseModel):
    category_name: str
    transaction_type: str
    total: Decimal
