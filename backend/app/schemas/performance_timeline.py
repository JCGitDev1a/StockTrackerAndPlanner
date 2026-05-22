from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class PortfolioTimelinePoint(BaseModel):
    date: date

    portfolio_value: Decimal

    model_config = {
        "from_attributes": True
    }
