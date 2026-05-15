from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models.account import Account
from app.models.account_position import AccountPosition
from app.models.security import Security
from app.models.user import User
from app.schemas.position import PositionCreateRequest, PositionResponse

router = APIRouter(prefix="/accounts/{account_id}/positions", tags=["positions"])


def get_owned_account(account_id: UUID, current_user: User, db: Session) -> Account:
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


@router.post("", response_model=PositionResponse, status_code=status.HTTP_201_CREATED)
def create_position(
    account_id: UUID,
    payload: PositionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    get_owned_account(account_id, current_user, db)

    security = db.query(Security).filter(Security.id == payload.security_id).first()

    if security is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Security not found",
        )

    existing_position = (
        db.query(AccountPosition)
        .filter(
            AccountPosition.account_id == account_id,
            AccountPosition.security_id == payload.security_id,
        )
        .first()
    )

    if existing_position:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Position already exists for this account/security",
        )

    position = AccountPosition(
        account_id=account_id,
        security_id=payload.security_id,
        drip_enabled=payload.drip_enabled,
        recurring_buy_enabled=payload.recurring_buy_enabled,
        is_watchlist=payload.is_watchlist,
    )

    db.add(position)
    db.commit()
    db.refresh(position)

    return position


@router.get("", response_model=list[PositionResponse])
def list_positions(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    get_owned_account(account_id, current_user, db)

    return (
        db.query(AccountPosition)
        .filter(
            AccountPosition.account_id == account_id,
            AccountPosition.deleted_at.is_(None),
        )
        .all()
    )
