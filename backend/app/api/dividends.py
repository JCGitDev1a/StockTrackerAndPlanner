from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.finance import (
    annualization_factor,
    quantize_money,
    quantize_price,
    quantize_shares,
)
from app.db.session import get_db
from app.models.dividend_event import DividendEvent
from app.models.security import Security
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.dividend import DividendProjectionResponse

router = APIRouter(prefix="/dividends", tags=["dividends"])


@router.get("/projections", response_model=list[DividendProjectionResponse])
def dividend_projections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    transactions = (
        db.query(Transaction, Security)
        .join(Security, Security.id == Transaction.security_id)
        .filter(Transaction.deleted_at.is_(None))
        .all()
    )

    holdings = {}

    for transaction, security in transactions:
        if security.id not in holdings:
            holdings[security.id] = {
                "symbol": security.symbol,
                "company": security.company,
                "dividend_frequency": security.dividend_frequency,
                "shares": Decimal("0"),
                "basis": Decimal("0"),
            }

        transaction_type = transaction.type.upper()

        if transaction_type in {"BUY", "DRIP_BUY"}:
            holdings[security.id]["shares"] += transaction.shares or Decimal("0")
            holdings[security.id]["basis"] += transaction.cash_amount or Decimal("0")

        elif transaction_type == "SELL":
            holdings[security.id]["shares"] -= transaction.shares or Decimal("0")
            holdings[security.id]["basis"] -= transaction.cash_amount or Decimal("0")

    results = []

    for security_id, holding in holdings.items():
        if holding["shares"] <= Decimal("0"):
            continue

        latest_dividend = (
            db.query(DividendEvent)
            .filter(DividendEvent.security_id == security_id)
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

            factor = annualization_factor(holding["dividend_frequency"])

            annual_dividend_per_share = latest_dividend.amount * factor
            annual_income = holding["shares"] * annual_dividend_per_share
            quarterly_income = annual_income / Decimal("4")
            monthly_income = annual_income / Decimal("12")

            if holding["basis"] > Decimal("0"):
                yield_on_cost = annual_income / holding["basis"]

        results.append(
            DividendProjectionResponse(
                symbol=holding["symbol"],
                company=holding["company"],
                dividend_frequency=holding["dividend_frequency"],
                shares=quantize_shares(holding["shares"]),
                latest_dividend_per_share=quantize_price(latest_dividend_per_share),
                annual_dividend_per_share=quantize_price(annual_dividend_per_share),
                annual_income=quantize_money(annual_income),
                quarterly_income=quantize_money(quarterly_income),
                monthly_income=quantize_money(monthly_income),
                yield_on_cost=quantize_price(yield_on_cost),
            )
        )

    return results
