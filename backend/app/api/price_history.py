from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models.price_history import PriceHistory

from app.models.security import Security
from app.models.user import User

from app.schemas.price_history import (
    PriceHistoryResponse,
)

router = APIRouter(
    prefix="/market-data/history",
    tags=["price-history"],
)


@router.get(
    "/{symbol}",
    response_model=list[PriceHistoryResponse],
)
def get_price_history(
    symbol: str,
    current_user: User = Depends(
        get_current_user
    ),
    db: Session = Depends(get_db),
):
    security = (
        db.query(Security)
        .filter(
            Security.symbol == symbol.upper()
        )
        .first()
    )

    if security is None:
        raise HTTPException(
            status_code=404,
            detail="Security not found",
        )

    return (
        db.query(PriceHistory)
        .filter(
            PriceHistory.security_id
            == security.id
        )
        .order_by(
            PriceHistory.price_date.asc()
        )
        .all()
    )
