from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db

from app.models.user import User
from app.schemas.transfer import TransferCreate, TransferResponse
from app.services import transfer_service
from app.services.auth_service import get_current_user



router = APIRouter(prefix="/transfers", tags=["transfers"])


@router.post("/", response_model=TransferResponse, status_code=status.HTTP_201_CREATED)
def create(data: TransferCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return transfer_service.create_transfer(db, current_user.id, data)


@router.get("/", response_model=list[TransferResponse])
def get_all(current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db)):
    return transfer_service.get_transfers(db, current_user.id)


@router.get("/{transfer_id}", response_model=TransferResponse)
def get_one(transfer_id: int,
            current_user: User = Depends(get_current_user),
            db: Session = Depends(get_db)):
    return transfer_service.get_transfer(db, current_user.id, transfer_id)




