from decimal import Decimal

from pydantic import BaseModel


class TransactionSummaryResponse(BaseModel):
    total_transactions: int

    buy_count: int
    sell_count: int
    dividend_count: int
    drip_buy_count: int

    total_buy_amount: Decimal
    total_sell_amount: Decimal
    total_dividend_amount: Decimal
