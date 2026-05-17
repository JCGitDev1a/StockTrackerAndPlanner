from decimal import Decimal

from pydantic import BaseModel


class AllocationResponse(BaseModel):
    symbol: str
    company: str

    market_value: Decimal
    allocation_percent: Decimal
