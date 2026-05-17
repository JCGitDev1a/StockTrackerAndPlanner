from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models.account import Account
from app.models.account_position import AccountPosition
from app.models.dividend_event import DividendEvent
from app.models.price_history import PriceHistory
from app.models.user import User
from app.schemas.dashboard_status import DashboardStatusResponse
from app.services.holdings_service import build_holdings_snapshot

router = APIRouter(
    prefix="/accounts/{account_id}/dashboard",
    tags=["dashboard-status"],
)


@router.get(
    "/status",
    response_model=DashboardStatusResponse,
)
def dashboard_status(
    account_id: UUID,
    as_of: date = Query(...),
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

    holdings_count = len(holdings)

    priced_holdings_count = 0
    fresh_price_count = 0
    stale_price_count = 0
    missing_price_count = 0

    dividend_covered_count = 0
    missing_dividend_count = 0

    for holding in holdings:
        latest_price = (
            db.query(PriceHistory)
            .filter(
                PriceHistory.security_id == holding["security_id"]
            )
            .order_by(PriceHistory.price_date.desc())
            .first()
        )

        if latest_price is None:
            missing_price_count += 1
        else:
            priced_holdings_count += 1

            if latest_price.price_date < as_of:
                stale_price_count += 1
            else:
                fresh_price_count += 1

        latest_dividend = (
            db.query(DividendEvent)
            .filter(
                DividendEvent.security_id == holding["security_id"]
            )
            .order_by(DividendEvent.pay_date.desc())
            .first()
        )

        if latest_dividend is None:
            missing_dividend_count += 1
        else:
            dividend_covered_count += 1

    watchlist_count = (
        db.query(AccountPosition)
        .filter(
            AccountPosition.account_id == account_id,
            AccountPosition.is_watchlist.is_(True),
            AccountPosition.deleted_at.is_(None),
        )
        .count()
    )

    return DashboardStatusResponse(
        holdings_count=holdings_count,
        watchlist_count=watchlist_count,
        priced_holdings_count=priced_holdings_count,
        fresh_price_count=fresh_price_count,
        stale_price_count=stale_price_count,
        missing_price_count=missing_price_count,
        dividend_covered_count=dividend_covered_count,
        missing_dividend_count=missing_dividend_count,
    )
