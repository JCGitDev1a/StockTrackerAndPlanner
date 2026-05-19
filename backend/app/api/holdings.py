from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models.account import Account
from app.models.user import User
from app.schemas.holding import HoldingResponse
from app.services.holdings_service import build_holdings_snapshot

router = APIRouter(prefix="/accounts/{account_id}/holdings", tags=["holdings"])


@router.get("", response_model=list[HoldingResponse])
def list_holdings(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = (
        db.query(Account)
        .filter(
            Account.id == account_id,
            Account.user_id == current_user.id,
        )
        .first()
    )

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    return build_holdings_snapshot(
        db=db,
        account_id=account_id,
    )

@router.get("/{symbol}", response_model=HoldingResponse)
def get_holding(
    account_id: UUID,
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = (
        db.query(Account)
        .filter(
            Account.id == account_id,
            Account.user_id == current_user.id,
        )
        .first()
    )

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    holdings = build_holdings_snapshot(
        db=db,
        account_id=account_id,
    )

    for holding in holdings:
        if holding["symbol"].upper() == symbol.upper():
            return holding

    raise HTTPException(status_code=404, detail="Holding not found")
