from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models.account import Account
from app.models.user import User
from app.schemas.account import AccountCreateRequest, AccountResponse

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(
    payload: AccountCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = Account(
        user_id=current_user.id,
        name=payload.name,
        account_type=payload.account_type,
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return account


@router.get("", response_model=list[AccountResponse])
def list_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Account).filter(Account.user_id == current_user.id).all()


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = (
        db.query(Account)
        .filter(Account.id == account_id, Account.user_id == current_user.id)
        .first()
    )

    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    return account
