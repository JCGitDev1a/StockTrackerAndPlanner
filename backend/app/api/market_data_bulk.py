from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models.price_history import PriceHistory
from app.models.security import Security
from app.models.user import User
from app.schemas.market_data_bulk import (
    BulkPriceImportResponse,
    BulkPriceItem,
)
from app.services.market_data_import_service import import_price_rows

router = APIRouter(
    prefix="/market-data",
    tags=["market-data-bulk"],
)


@router.post(
    "/bulk-prices",
    response_model=BulkPriceImportResponse,
)
def bulk_price_import(
    payload: list[BulkPriceItem],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    created = []
    skipped = []
    missing_securities = []

    rows = [
        {
            "symbol": item.symbol,
            "price_date": item.price_date,
            "price": item.price,
        }
        for item in payload
    ]

    result = import_price_rows(
        db=db,
        rows=rows,
        source_provider="manual",
    )

    return BulkPriceImportResponse(
        created=result["created"],
        updated=result["updated"],
        skipped=[],
        missing_securities=result["missing_securities"],
    )
