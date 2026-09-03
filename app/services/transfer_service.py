from sqlalchemy.orm import Session

from app.models import Account
from app.schemas.transfer import TransferCreate
from app.models.transfer import Transfer
from app.services.exchange_rate_service import get_rate
from app.exceptions import NotFoundException, BadRequestException



def create_transfer(db: Session, user_id: int, data: TransferCreate) -> Transfer:
    if data.source_account_id == data.destination_account_id:
        raise BadRequestException("Source and destination accounts cannot be the same")

    # get currency rate for source and destination accounts
    source_account = db.query(Account).filter(Account.id == data.source_account_id, Account.user_id == user_id).first()
    if not source_account:
        raise NotFoundException("Source account not found")

    destination_account = db.query(Account).filter(Account.id == data.destination_account_id, Account.user_id == user_id).first()
    if not destination_account:
        raise NotFoundException("Destination account not found")

    rate = get_rate(db, source_account.currency, destination_account.currency, data.transfer_date)
    destination_amount = data.source_amount * rate

    transfer = Transfer(**data.model_dump(), user_id=user_id, destination_amount=destination_amount)
    db.add(transfer)
    db.commit()
    db.refresh(transfer)
    return transfer


def get_transfer(db: Session, user_id: int, transfer_id: int) -> Transfer:
    transfer = db.query(Transfer).filter(Transfer.user_id == user_id, Transfer.id == transfer_id).first()

    if not transfer:
        raise NotFoundException("Transfer not found")

    return transfer


def get_transfers(db: Session, user_id: int) -> list[Transfer]:
    transfers = db.query(Transfer).filter(Transfer.user_id == user_id).all()
    return transfers