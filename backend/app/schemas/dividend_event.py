from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class DividendEventCreateRequest(BaseModel):
    security_id: UUID
    ex_date: date | None = None
    pay_date: date
    amount: Decimal
    source_provider: str = "manual"


class DividendEventResponse(BaseModel):
    id: UUID
    security_id: UUID
    ex_date: date | None
    pay_date: date
    amount: Decimal
    source_provider: str
    source_timestamp: datetime
    is_manual_override: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
