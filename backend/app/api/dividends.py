from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.finance import (
    annualization_factor,
    quantize_money,
    quantize_price,
)
from app.db.session import get_db
from app.models.account import Account
from app.models.dividend_event import DividendEvent
from app.models.security import Security
from app.models.user import User
from app.schemas.dividend import DividendProjectionResponse
from app.services.holdings_service import build_holdings_snapshot

router = APIRouter(
    prefix="/accounts/{account_id}/dividends",
    tags=["dividends"],
)


@router.get("/projections", response_model=list[DividendProjectionResponse])
def dividend_projections(
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
        latest_dividend = (
            db.query(DividendEvent)
            .join(Security, Security.id == DividendEvent.security_id)
            .filter(Security.symbol == holding["symbol"])
            .order_by(DividendEvent.pay_date.desc())
            .first()
        )

        latest_dividend_per_share = None
        annual_dividend_per_share = None
        annual_income = None
        quarterly_income = None
        monthly_income = None
        yield_on_cost = None

        if latest_dividend is not None:
            latest_dividend_per_share = latest_dividend.amount

            factor = annualization_factor(
                holding["dividend_frequency"]
            )

            annual_dividend_per_share = latest_dividend.amount * factor
            annual_income = holding["shares"] * annual_dividend_per_share
            quarterly_income = annual_income / Decimal("4")
            monthly_income = annual_income / Decimal("12")

            if holding["total_basis"] > Decimal("0"):
                yield_on_cost = annual_income / holding["total_basis"]

        results.append(
            DividendProjectionResponse(
                symbol=holding["symbol"],
                company=holding["company"],
                dividend_frequency=holding["dividend_frequency"],
                shares=holding["shares"],
                latest_dividend_per_share=quantize_price(
                    latest_dividend_per_share
                ),
                annual_dividend_per_share=quantize_price(
                    annual_dividend_per_share
                ),
                annual_income=quantize_money(annual_income),
                quarterly_income=quantize_money(quarterly_income),
                monthly_income=quantize_money(monthly_income),
                yield_on_cost=quantize_price(yield_on_cost),
            )
        )

    return results
