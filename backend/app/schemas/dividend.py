from decimal import Decimal

from pydantic import BaseModel


class DividendProjectionResponse(BaseModel):
    symbol: str
    company: str
    dividend_frequency: str | None

    shares: Decimal

    latest_dividend_per_share: Decimal | None
    annual_dividend_per_share: Decimal | None

    annual_income: Decimal | None
    quarterly_income: Decimal | None
    monthly_income: Decimal | None

    yield_on_cost: Decimal | None
