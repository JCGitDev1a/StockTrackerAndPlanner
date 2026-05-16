from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class PriceCreateRequest(BaseModel):
    security_id: UUID
    price_date: date
    price: Decimal
    source_provider: str = "manual"

class PriceResponse(BaseModel):
    id: UUID
    security_id: UUID
    price_date: date
    price: Decimal
    source_provider: str
    source_timestamp: datetime
    is_manual_override: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class LatestPriceResponse(BaseModel):
    security_id: UUID
    symbol: str
    company: str
    price_date: date
    price: Decimal
    source_provider: str
