from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class HoldingResponse(BaseModel):
    security_id: UUID
    symbol: str
    company: str
    shares: Decimal
    total_basis: Decimal | None
    average_cost: Decimal | None
    current_price: Decimal | None
    market_value: Decimal | None
    unrealized_gain_loss: Decimal | None
