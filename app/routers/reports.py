from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.report import MonthlySummary, CategorySummary
from app.services import report_service
from app.services.auth_service import get_current_user
from app.models.user import User

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/monthly", response_model=MonthlySummary)
def monthly_summary(year: int, month: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> MonthlySummary:
    return report_service.get_monthly_summary(db, current_user.id, year, month)


@router.get("/categories", response_model=list[CategorySummary])
def category_summary(year: int, month: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[CategorySummary]:
    return report_service.get_category_summary(db, current_user.id, year, month)
