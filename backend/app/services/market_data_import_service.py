from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.price_history import PriceHistory
from app.models.security import Security


def get_security_by_symbol(
    db: Session,
    symbol: str,
) -> Security | None:
    return (
        db.query(Security)
        .filter(Security.symbol == symbol.upper())
        .first()
    )


def price_exists(
    db: Session,
    security_id,
    price_date: date,
) -> bool:
    return (
        db.query(PriceHistory)
        .filter(
            PriceHistory.security_id == security_id,
            PriceHistory.price_date == price_date,
        )
        .first()
        is not None
    )


def upsert_price(
    db: Session,
    symbol: str,
    price_date: date,
    price: Decimal,
    source_provider: str = "manual",
) -> str:
    security = get_security_by_symbol(
        db=db,
        symbol=symbol,
    )

    if security is None:
        return "missing_security"

    existing = (
        db.query(PriceHistory)
        .filter(
            PriceHistory.security_id == security.id,
            PriceHistory.price_date == price_date,
        )
        .first()
    )

    if existing is not None:
        existing.price = price
        existing.source_provider = source_provider
        existing.source_timestamp = datetime.now(timezone.utc)
        existing.is_manual_override = source_provider == "manual"

        db.flush()

        return "updated"

    price_history = PriceHistory(
        security_id=security.id,
        price_date=price_date,
        price=price,
        source_provider=source_provider,
        source_timestamp=datetime.now(timezone.utc),
        is_manual_override=source_provider == "manual",
    )

    db.add(price_history)
    db.flush()

    return "created"


def import_price_rows(
    db: Session,
    rows: list[dict],
    source_provider: str = "manual",
) -> dict:
    created: list[str] = []
    updated: list[str] = []
    missing_securities: list[str] = []
    invalid_rows: list[dict] = []

    for row in rows:
        try:
            symbol = str(row["symbol"]).strip().upper()
            price_date = row["price_date"]
            price = Decimal(str(row["price"]))

            if isinstance(price_date, str):
                price_date = date.fromisoformat(price_date)

            result = upsert_price(
                db=db,
                symbol=symbol,
                price_date=price_date,
                price=price,
                source_provider=source_provider,
            )

            if result == "created":
                created.append(symbol)
            elif result == "updated":
                updated.append(symbol)
            elif result == "missing_security":
                missing_securities.append(symbol)

        except Exception as exc:
            invalid_rows.append(
                {
                    "row": row,
                    "error": str(exc),
                }
            )

    db.commit()

    return {
        "created": sorted(set(created)),
        "updated": sorted(set(updated)),
        "missing_securities": sorted(set(missing_securities)),
        "invalid_rows": invalid_rows,
    }
