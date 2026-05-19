from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models.account import Account
from app.models.security import Security
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import TransactionCreateRequest, TransactionResponse

router = APIRouter(prefix="/accounts/{account_id}/transactions", tags=["transactions"])


def get_owned_account(account_id: UUID, current_user: User, db: Session) -> Account:
    account = (
        db.query(Account)
        .filter(Account.id == account_id, Account.user_id == current_user.id)
        .first()
    )

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    return account


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    account_id: UUID,
    payload: TransactionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    get_owned_account(account_id, current_user, db)

    security = db.query(Security).filter(Security.id == payload.security_id).first()

    if security is None:
        raise HTTPException(status_code=404, detail="Security not found")

    transaction = Transaction(
        account_id=account_id,
        security_id=payload.security_id,
        type=payload.type.upper(),
        shares=payload.shares,
        price=payload.price,
        cash_amount=payload.cash_amount,
        transaction_date=payload.transaction_date,
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


@router.get("", response_model=list[TransactionResponse])
def list_transactions(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    get_owned_account(account_id, current_user, db)

    return (
        db.query(Transaction)
        .filter(
            Transaction.account_id == account_id,
            Transaction.deleted_at.is_(None),
        )
        .order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
        .all()
    )

@router.get("/symbol/{symbol}", response_model=list[TransactionResponse])
def list_transactions_by_symbol(
    account_id: UUID,
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    get_owned_account(account_id, current_user, db)

    security = (
        db.query(Security)
        .filter(Security.symbol == symbol.upper())
        .first()
    )

    if security is None:
        raise HTTPException(status_code=404, detail="Security not found")

    return (
        db.query(Transaction)
        .filter(
            Transaction.account_id == account_id,
            Transaction.security_id == security.id,
            Transaction.deleted_at.is_(None),
        )
        .order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
        .all()
    )
