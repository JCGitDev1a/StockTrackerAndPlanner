from decimal import Decimal

from pydantic import BaseModel


class PortfolioSummaryResponse(BaseModel):
    total_market_value: Decimal
    total_cost_basis: Decimal
    total_unrealized_gain_loss: Decimal

    monthly_dividend_income: Decimal
    quarterly_dividend_income: Decimal
    annual_dividend_income: Decimal

    holdings_count: int
    watchlist_count: int
