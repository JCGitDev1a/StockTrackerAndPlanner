from pydantic import BaseModel


class MissingPriceResponse(BaseModel):
    symbol: str
    company: str
