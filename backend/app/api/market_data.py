from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models.price_history import PriceHistory
from app.models.security import Security
from app.models.user import User
from app.schemas.market_data import (
    LatestPriceResponse,
    PriceCreateRequest,
    PriceResponse,
)

router = APIRouter(prefix="/market-data", tags=["market-data"])


@router.post("/price", response_model=PriceResponse, status_code=status.HTTP_201_CREATED)
def create_price(
    payload: PriceCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    security = (
        db.query(Security)
        .filter(Security.id == payload.security_id)
        .first()
    )

    if security is None:
        raise HTTPException(status_code=404, detail="Security not found")

    existing_price = (
        db.query(PriceHistory)
        .filter(
            PriceHistory.security_id == payload.security_id,
            PriceHistory.price_date == payload.price_date,
        )
        .first()
    )

    if existing_price:
        raise HTTPException(
            status_code=400,
            detail="Price already exists for this security/date",
        )

    price = PriceHistory(
        security_id=payload.security_id,
        price_date=payload.price_date,
        price=payload.price,
        source_provider=payload.source_provider,
        source_timestamp=datetime.now(timezone.utc),
        is_manual_override=True,
    )

    db.add(price)
    db.commit()
    db.refresh(price)

    return price


@router.get("/latest/{symbol}", response_model=LatestPriceResponse)
def get_latest_price(
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    security = (
        db.query(Security)
        .filter(Security.symbol == symbol.upper())
        .first()
    )

    if security is None:
        raise HTTPException(status_code=404, detail="Security not found")

    latest_price = (
        db.query(PriceHistory)
        .filter(PriceHistory.security_id == security.id)
        .order_by(PriceHistory.price_date.desc())
        .first()
    )

    if latest_price is None:
        raise HTTPException(status_code=404, detail="No price history found")

    return LatestPriceResponse(
        security_id=security.id,
        symbol=security.symbol,
        company=security.company,
        price_date=latest_price.price_date,
        price=latest_price.price,
        source_provider=latest_price.source_provider,
    )
