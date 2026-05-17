from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.finance import annualization_factor, quantize_money
from app.models.account_position import AccountPosition
from app.models.dividend_event import DividendEvent
from app.models.price_history import PriceHistory
from app.models.security import Security
from app.models.transaction import Transaction
from app.schemas.dashboard import PortfolioSummaryResponse


def calculate_portfolio_summary(
    db: Session,
    account_id: UUID,
) -> PortfolioSummaryResponse:
    transactions = (
        db.query(Transaction, Security)
        .join(Security, Security.id == Transaction.security_id)
        .filter(
            Transaction.account_id == account_id,
            Transaction.deleted_at.is_(None),
        )
        .all()
    )

    holdings = {}

    for transaction, security in transactions:
        if security.id not in holdings:
            holdings[security.id] = {
                "shares": Decimal("0"),
                "basis": Decimal("0"),
                "frequency": security.dividend_frequency,
            }

        transaction_type = transaction.type.upper()

        if transaction_type in {"BUY", "DRIP_BUY"}:
            holdings[security.id]["shares"] += transaction.shares or Decimal("0")
            holdings[security.id]["basis"] += transaction.cash_amount or Decimal("0")

        elif transaction_type == "SELL":
            holdings[security.id]["shares"] -= transaction.shares or Decimal("0")
            holdings[security.id]["basis"] -= transaction.cash_amount or Decimal("0")

    total_market_value = Decimal("0")
    total_cost_basis = Decimal("0")
    total_unrealized_gain_loss = Decimal("0")

    monthly_dividend_income = Decimal("0")
    quarterly_dividend_income = Decimal("0")
    annual_dividend_income = Decimal("0")

    holdings_count = 0

    for security_id, holding in holdings.items():
        if holding["shares"] <= Decimal("0"):
            continue

        holdings_count += 1

        latest_price = (
            db.query(PriceHistory)
            .filter(PriceHistory.security_id == security_id)
            .order_by(PriceHistory.price_date.desc())
            .first()
        )

        if latest_price is not None:
            market_value = holding["shares"] * latest_price.price

            total_market_value += market_value
            total_cost_basis += holding["basis"]
            total_unrealized_gain_loss += market_value - holding["basis"]

        latest_dividend = (
            db.query(DividendEvent)
            .filter(DividendEvent.security_id == security_id)
            .order_by(DividendEvent.pay_date.desc())
            .first()
        )

        if latest_dividend is not None:
            factor = annualization_factor(holding["frequency"])

            annual_income = holding["shares"] * latest_dividend.amount * factor

            annual_dividend_income += annual_income
            quarterly_dividend_income += annual_income / Decimal("4")
            monthly_dividend_income += annual_income / Decimal("12")

    watchlist_count = (
        db.query(AccountPosition)
        .filter(
            AccountPosition.account_id == account_id,
            AccountPosition.is_watchlist.is_(True),
            AccountPosition.deleted_at.is_(None),
        )
        .count()
    )

    return PortfolioSummaryResponse(
        total_market_value=quantize_money(total_market_value),
        total_cost_basis=quantize_money(total_cost_basis),
        total_unrealized_gain_loss=quantize_money(total_unrealized_gain_loss),
        monthly_dividend_income=quantize_money(monthly_dividend_income),
        quarterly_dividend_income=quantize_money(quarterly_dividend_income),
        annual_dividend_income=quantize_money(annual_dividend_income),
        holdings_count=holdings_count,
        watchlist_count=watchlist_count,
    )
