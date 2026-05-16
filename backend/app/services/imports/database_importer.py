from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.account_position import AccountPosition
from app.models.security import Security
from app.models.transaction import Transaction
from app.services.imports.models import ImportedHolding


def get_or_create_security(
    db: Session,
    symbol: str,
    company: str,
) -> Security:
    security = db.query(Security).filter(Security.symbol == symbol.upper()).first()

    if security:
        return security

    security = Security(
        symbol=symbol.upper(),
        company=company,
    )

    db.add(security)
    db.flush()

    return security


def get_or_create_position(
    db: Session,
    account_id,
    security_id,
    is_watchlist: bool,
) -> AccountPosition:
    position = (
        db.query(AccountPosition)
        .filter(
            AccountPosition.account_id == account_id,
            AccountPosition.security_id == security_id,
        )
        .first()
    )

    if position:
        return position

    position = AccountPosition(
        account_id=account_id,
        security_id=security_id,
        drip_enabled=True,
        recurring_buy_enabled=True,
        is_watchlist=is_watchlist,
    )

    db.add(position)
    db.flush()

    return position


def opening_buy_exists(
    db: Session,
    account_id,
    security_id,
    holding: ImportedHolding,
    start_date: date,
) -> bool:
    existing = (
        db.query(Transaction)
        .filter(
            Transaction.account_id == account_id,
            Transaction.security_id == security_id,
            Transaction.type == "BUY",
            Transaction.transaction_date == start_date,
            Transaction.shares == holding.quantity,
            Transaction.price == holding.price,
            Transaction.cash_amount == holding.quantity * holding.price,
            Transaction.deleted_at.is_(None),
        )
        .first()
    )

    return existing is not None


def create_opening_buy_transaction(
    db: Session,
    account_id,
    security_id,
    holding: ImportedHolding,
    start_date: date,
) -> Transaction | None:
    if holding.quantity <= Decimal("0"):
        return None

    if opening_buy_exists(
        db=db,
        account_id=account_id,
        security_id=security_id,
        holding=holding,
        start_date=start_date,
    ):
        return None

    transaction = Transaction(
        account_id=account_id,
        security_id=security_id,
        type="BUY",
        shares=holding.quantity,
        price=holding.price,
        cash_amount=holding.quantity * holding.price,
        transaction_date=start_date,
    )

    db.add(transaction)
    db.flush()

    return transaction


def import_holdings(
    db: Session,
    account_id,
    holdings: list[ImportedHolding],
    start_date: date,
) -> dict:
    created_securities: list[str] = []
    reused_securities: list[str] = []
    created_positions: list[str] = []
    reused_positions: list[str] = []
    created_transactions: int = 0
    skipped_transactions: int = 0
    watchlist_items: list[str] = []

    for holding in holdings:
        security_exists = (
            db.query(Security)
            .filter(Security.symbol == holding.symbol.upper())
            .first()
        )

        security = get_or_create_security(
            db=db,
            symbol=holding.symbol,
            company=holding.company,
        )

        if security_exists:
            reused_securities.append(security.symbol)
        else:
            created_securities.append(security.symbol)

        is_watchlist = holding.quantity == Decimal("0")

        position_exists = (
            db.query(AccountPosition)
            .filter(
                AccountPosition.account_id == account_id,
                AccountPosition.security_id == security.id,
            )
            .first()
        )

        get_or_create_position(
            db=db,
            account_id=account_id,
            security_id=security.id,
            is_watchlist=is_watchlist,
        )

        if position_exists:
            reused_positions.append(security.symbol)
        else:
            created_positions.append(security.symbol)

        if is_watchlist:
            watchlist_items.append(security.symbol)
            continue

        transaction = create_opening_buy_transaction(
            db=db,
            account_id=account_id,
            security_id=security.id,
            holding=holding,
            start_date=start_date,
        )

        if transaction is None:
            skipped_transactions += 1
        else:
            created_transactions += 1

    db.commit()

    return {
        "created_securities": sorted(set(created_securities)),
        "reused_securities": sorted(set(reused_securities)),
        "created_positions": sorted(set(created_positions)),
        "reused_positions": sorted(set(reused_positions)),
        "created_transactions": created_transactions,
        "skipped_transactions": skipped_transactions,
        "watchlist_items": sorted(set(watchlist_items)),
    }
