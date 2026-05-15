from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PositionCreateRequest(BaseModel):
    security_id: UUID
    drip_enabled: bool = True
    recurring_buy_enabled: bool = True
    is_watchlist: bool = False


class PositionResponse(BaseModel):
    id: UUID
    account_id: UUID
    security_id: UUID
    drip_enabled: bool
    recurring_buy_enabled: bool
    is_watchlist: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
