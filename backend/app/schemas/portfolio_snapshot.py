from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class PortfolioSnapshotResponse(BaseModel):
    id: UUID

    account_id: UUID
    snapshot_date: date

    market_value: Decimal
    cost_basis: Decimal
    unrealized_gain_loss: Decimal

    monthly_dividend_income: Decimal
    annual_dividend_income: Decimal

    holdings_count: int
    watchlist_count: int

    created_at: datetime

    model_config = {
        "from_attributes": True
    }
