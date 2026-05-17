from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models.account import Account
from app.models.price_history import PriceHistory
from app.models.user import User
from app.schemas.market_data_stale import StalePriceResponse
from app.services.holdings_service import build_holdings_snapshot

router = APIRouter(
    prefix="/accounts/{account_id}/market-data",
    tags=["market-data-stale"],
)


@router.get(
    "/stale-prices",
    response_model=list[StalePriceResponse],
)
def stale_prices(
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

    results = []

    for holding in holdings:
        latest_price = (
            db.query(PriceHistory)
            .filter(
                PriceHistory.security_id == holding["security_id"]
            )
            .order_by(PriceHistory.price_date.desc())
            .first()
        )

        latest_price_date = (
            latest_price.price_date
            if latest_price is not None
            else None
        )

        if latest_price_date is None or latest_price_date < as_of:
            results.append(
                StalePriceResponse(
                    symbol=holding["symbol"],
                    company=holding["company"],
                    latest_price_date=latest_price_date,
                )
            )

    results.sort(key=lambda item: item.symbol)

    return results
