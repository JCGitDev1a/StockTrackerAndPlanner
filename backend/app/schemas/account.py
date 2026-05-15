from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AccountCreateRequest(BaseModel):
    name: str
    account_type: str


class AccountResponse(BaseModel):
    id: UUID
    name: str
    account_type: str
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
