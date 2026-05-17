from datetime import date

from pydantic import BaseModel


class StalePriceResponse(BaseModel):
    symbol: str
    company: str
    latest_price_date: date | None
