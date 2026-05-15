from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class TransactionCreateRequest(BaseModel):
    security_id: UUID
    type: str
    shares: Decimal | None = None
    price: Decimal | None = None
    cash_amount: Decimal | None = None
    transaction_date: date


class TransactionResponse(BaseModel):
    id: UUID
    account_id: UUID
    security_id: UUID
    type: str
    shares: Decimal | None
    price: Decimal | None
    cash_amount: Decimal | None
    transaction_date: date
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
