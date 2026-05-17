from decimal import Decimal

from pydantic import BaseModel


class PerformanceSummaryResponse(BaseModel):
    current_market_value: Decimal
    current_cost_basis: Decimal
    current_gain_loss: Decimal
    current_gain_loss_percent: Decimal | None
