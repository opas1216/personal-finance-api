from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.account import AccountCreate, AccountUpdate, AccountResponse
from app.services import account_service

router = APIRouter(prefix="/accounts", tags=["accounts"])

#   FastAPI 判斷一個參數是 path parameter 還是 query parameter 的規則很簡單：
#
#   - 出現在路徑 /{user_id} → path parameter
#   - 只在函數參數裡，沒有在路徑裡 → query parameter（自動）

@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create(data: AccountCreate, db: Session = Depends(get_db)):
    return account_service.create_account(db, data)


# Query parameter user_id is used to filter accounts by user_id
# GET /accounts?user_id=1
@router.get("/", response_model=list[AccountResponse])
def get_all(user_id: int, db: Session = Depends(get_db)):
    return account_service.get_accounts(db, user_id)


# path parameter account_id is used to get a specific account by its ID
# GET /accounts/5
@router.get("/{account_id}", response_model=AccountResponse)
def get_one(account_id: int, db: Session = Depends(get_db)):
    return account_service.get_account(db, account_id)

@router.put("/{account_id}", response_model=AccountResponse)
def update_account(account_id: int, data: AccountUpdate, db: Session = Depends(get_db)):
    return account_service.update_account(db, account_id, data)

@router.delete("/{account_id}", status_code=204)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    account_service.delete_account(db, account_id)