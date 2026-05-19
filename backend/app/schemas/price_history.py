from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class PriceHistoryResponse(BaseModel):
    security_id: UUID
    price_date: date
    price: Decimal
    source_provider: str

    class Config:
        from_attributes = True
