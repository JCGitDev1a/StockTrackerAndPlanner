from pydantic import BaseModel


class DashboardStatusResponse(BaseModel):
    holdings_count: int
    watchlist_count: int

    priced_holdings_count: int
    fresh_price_count: int
    stale_price_count: int
    missing_price_count: int

    dividend_covered_count: int
    missing_dividend_count: int
