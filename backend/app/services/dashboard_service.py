from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.finance import annualization_factor, quantize_money
from app.models.account_position import AccountPosition
from app.models.dividend_event import DividendEvent
from app.models.security import Security
from app.schemas.dashboard import PortfolioSummaryResponse
from app.services.holdings_service import build_holdings_snapshot


def calculate_portfolio_summary(
    db: Session,
    account_id: UUID,
) -> PortfolioSummaryResponse:
    holdings = build_holdings_snapshot(
        db=db,
        account_id=account_id,
    )

    total_market_value = Decimal("0")
    total_cost_basis = Decimal("0")
    total_unrealized_gain_loss = Decimal("0")

    monthly_dividend_income = Decimal("0")
    quarterly_dividend_income = Decimal("0")
    annual_dividend_income = Decimal("0")

    holdings_count = 0

    for holding in holdings:
        holdings_count += 1

        total_market_value += holding["market_value"] or Decimal("0")
        total_cost_basis += holding["total_basis"] or Decimal("0")
        total_unrealized_gain_loss += holding["unrealized_gain_loss"] or Decimal("0")

        latest_dividend = (
            db.query(DividendEvent)
            .join(Security, Security.id == DividendEvent.security_id)
            .filter(Security.symbol == holding["symbol"])
            .order_by(DividendEvent.pay_date.desc())
            .first()
        )

        if latest_dividend is not None:
            factor = annualization_factor(
                holding["dividend_frequency"]
            )

            annual_income = (
                holding["shares"]
                * latest_dividend.amount
                * factor
            )

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
