from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.finance import quantize_money, quantize_price
from app.db.session import get_db
from app.models.account import Account
from app.models.user import User
from app.schemas.allocation import AllocationResponse
from app.services.holdings_service import build_holdings_snapshot

router = APIRouter(
    prefix="/accounts/{account_id}/allocation",
    tags=["allocation"],
)


@router.get("", response_model=list[AllocationResponse])
def portfolio_allocation(
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

    total_market_value = sum(
        holding["market_value"] or Decimal("0")
        for holding in holdings
    )

    results = []

    for holding in holdings:
        market_value = holding["market_value"] or Decimal("0")

        allocation_percent = (
            (market_value / total_market_value) * Decimal("100")
            if total_market_value > Decimal("0")
            else Decimal("0")
        )

        results.append(
            AllocationResponse(
                symbol=holding["symbol"],
                company=holding["company"],
                market_value=quantize_money(market_value),
                allocation_percent=quantize_price(allocation_percent),
            )
        )

    results.sort(
        key=lambda item: item.market_value,
        reverse=True,
    )

    return results
