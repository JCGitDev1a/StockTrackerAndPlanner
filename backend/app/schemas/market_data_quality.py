from pydantic import BaseModel


class MarketDataQualityResponse(BaseModel):
    holdings_count: int

    priced_holdings_count: int
    missing_price_count: int

    stale_price_count: int
    fresh_price_count: int
