from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.finance import quantize_money, quantize_price
from app.db.session import get_db
from app.models.account import Account
from app.models.user import User
from app.schemas.performance import PerformanceSummaryResponse
from app.services.holdings_service import build_holdings_snapshot

from app.schemas.performance_timeline import PortfolioTimelinePoint
from app.services.portfolio_timeline_service import build_portfolio_timeline

router = APIRouter(
    prefix="/accounts/{account_id}/performance",
    tags=["performance"],
)


@router.get("/summary", response_model=PerformanceSummaryResponse)
def performance_summary(
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

    current_market_value = Decimal("0")
    current_cost_basis = Decimal("0")
    current_gain_loss = Decimal("0")

    for holding in holdings:
        current_market_value += (
            holding["market_value"] or Decimal("0")
        )

        current_cost_basis += (
            holding["total_basis"] or Decimal("0")
        )

        current_gain_loss += (
            holding["unrealized_gain_loss"] or Decimal("0")
        )

    current_gain_loss_percent = None

    if current_cost_basis > Decimal("0"):
        current_gain_loss_percent = (
            current_gain_loss / current_cost_basis
        ) * Decimal("100")

    return PerformanceSummaryResponse(
        current_market_value=quantize_money(
            current_market_value
        ),
        current_cost_basis=quantize_money(
            current_cost_basis
        ),
        current_gain_loss=quantize_money(
            current_gain_loss
        ),
        current_gain_loss_percent=quantize_price(
            current_gain_loss_percent
        ),
    )

@router.get(
    "/timeline",
    response_model=list[PortfolioTimelinePoint],
)
def performance_timeline(
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

    return build_portfolio_timeline(
        db=db,
        account_id=account_id,
    )
