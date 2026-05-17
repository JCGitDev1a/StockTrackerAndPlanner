from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models.account import Account
from app.models.user import User
from app.schemas.market_data_missing import MissingPriceResponse
from app.services.holdings_service import build_holdings_snapshot

router = APIRouter(
    prefix="/accounts/{account_id}/market-data",
    tags=["market-data-admin"],
)


@router.get(
    "/missing-prices",
    response_model=list[MissingPriceResponse],
)
def missing_prices(
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

    holdings = build_holdings_snapshot(
        db=db,
        account_id=account_id,
    )

    results = []

    for holding in holdings:
        if holding["current_price"] is not None:
            continue

        results.append(
            MissingPriceResponse(
                symbol=holding["symbol"],
                company=holding["company"],
            )
        )

    results.sort(key=lambda item: item.symbol)

    return results
