from collections import defaultdict
from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.finance import quantize_money
from app.models.price_history import PriceHistory
from app.models.security import Security
from app.models.transaction import Transaction


def build_share_positions_as_of(
    db: Session,
    account_id: UUID,
    as_of_date: date,
) -> dict[UUID, Decimal]:
    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.account_id == account_id,
            Transaction.transaction_date <= as_of_date,
            Transaction.deleted_at.is_(None),
        )
        .all()
    )

    positions: dict[UUID, Decimal] = defaultdict(
        lambda: Decimal("0")
    )

    for transaction in transactions:
        transaction_type = transaction.type.upper()

        if transaction_type in {"BUY", "DRIP_BUY"}:
            positions[transaction.security_id] += (
                transaction.shares or Decimal("0")
            )

        elif transaction_type == "SELL":
            positions[transaction.security_id] -= (
                transaction.shares or Decimal("0")
            )

    return {
        security_id: shares
        for security_id, shares in positions.items()
        if shares > Decimal("0")
    }


def build_portfolio_timeline(
    db: Session,
    account_id: UUID,
) -> list[dict]:
    price_dates = (
        db.query(PriceHistory.price_date)
        .join(Security, Security.id == PriceHistory.security_id)
        .join(Transaction, Transaction.security_id == Security.id)
        .filter(
            Transaction.account_id == account_id,
            Transaction.deleted_at.is_(None),
        )
        .distinct()
        .order_by(PriceHistory.price_date.asc())
        .all()
    )

    results = []

    for row in price_dates:
        price_date = row[0]

        positions = build_share_positions_as_of(
            db=db,
            account_id=account_id,
            as_of_date=price_date,
        )

        portfolio_value = Decimal("0")

        for security_id, shares in positions.items():
            latest_price = (
                db.query(PriceHistory)
                .filter(
                    PriceHistory.security_id == security_id,
                    PriceHistory.price_date <= price_date,
                )
                .order_by(PriceHistory.price_date.desc())
                .first()
            )

            if latest_price is None:
                continue

            portfolio_value += shares * latest_price.price

        results.append(
            {
                "date": price_date,
                "portfolio_value": quantize_money(
                    portfolio_value
                ),
            }
        )

    return results
