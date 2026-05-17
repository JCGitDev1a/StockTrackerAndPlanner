from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class BulkPriceItem(BaseModel):
    symbol: str
    price_date: date
    price: Decimal
    source_provider: str = "manual"


class BulkPriceImportResponse(BaseModel):
    created: list[str]
    skipped: list[str]
    missing_securities: list[str]
