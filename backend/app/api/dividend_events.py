from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models.dividend_event import DividendEvent
from app.models.security import Security
from app.models.user import User
from app.schemas.dividend_event import (
    DividendEventCreateRequest,
    DividendEventResponse,
)

from app.models.account import Account

def get_owned_account(account_id: UUID, current_user: User, db: Session) -> Account:
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

    return account

router = APIRouter(prefix="/dividend-events", tags=["dividend-events"])


@router.post("", response_model=DividendEventResponse, status_code=status.HTTP_201_CREATED)
def create_dividend_event(
    payload: DividendEventCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    security = db.query(Security).filter(Security.id == payload.security_id).first()

    if security is None:
        raise HTTPException(status_code=404, detail="Security not found")

    event = DividendEvent(
        security_id=payload.security_id,
        ex_date=payload.ex_date,
        pay_date=payload.pay_date,
        amount=payload.amount,
        source_provider=payload.source_provider,
        source_timestamp=datetime.now(timezone.utc),
        is_manual_override=True,
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return event


@router.get("/{symbol}", response_model=list[DividendEventResponse])
def list_dividend_events(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    security = db.query(Security).filter(Security.symbol == symbol.upper()).first()

    if security is None:
        raise HTTPException(status_code=404, detail="Security not found")

    return (
        db.query(DividendEvent)
        .filter(DividendEvent.security_id == security.id)
        .order_by(DividendEvent.pay_date.desc())
        .all()
    )

@router.get(
    "/symbol/{symbol}",
    response_model=list[DividendEventResponse],
)
def list_dividend_events_by_symbol(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    security = (
        db.query(Security)
        .filter(
            Security.symbol == symbol.upper()
        )
        .first()
    )

    if security is None:
        raise HTTPException(
            status_code=404,
            detail="Security not found",
        )

    return (
        db.query(DividendEvent)
        .filter(
            DividendEvent.security_id == security.id,
        )
        .order_by(
            DividendEvent.pay_date.desc()
        )
        .all()
    )
