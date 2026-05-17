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

    for item in payload:
        security = (
            db.query(Security)
            .filter(Security.symbol == item.symbol.upper())
            .first()
        )

        if security is None:
            missing_securities.append(item.symbol.upper())
            continue

        existing = (
            db.query(PriceHistory)
            .filter(
                PriceHistory.security_id == security.id,
                PriceHistory.price_date == item.price_date,
            )
            .first()
        )

        if existing is not None:
            skipped.append(item.symbol.upper())
            continue

        price = PriceHistory(
            security_id=security.id,
            price_date=item.price_date,
            price=item.price,
            source_provider=item.source_provider,
            source_timestamp=datetime.now(timezone.utc),
            is_manual_override=True,
        )

        db.add(price)

        created.append(item.symbol.upper())

    db.commit()

    return BulkPriceImportResponse(
        created=sorted(set(created)),
        skipped=sorted(set(skipped)),
        missing_securities=sorted(set(missing_securities)),
    )
