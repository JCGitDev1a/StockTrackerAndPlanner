from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SecurityCreateRequest(BaseModel):
    symbol: str
    company: str
    dividend_frequency: str | None = None


class SecurityResponse(BaseModel):
    id: UUID
    symbol: str
    company: str
    dividend_frequency: str | None
    is_active: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
