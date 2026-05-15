from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models.account import Account
from app.models.security import Security
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.holding import HoldingResponse

router = APIRouter(prefix="/accounts/{account_id}/holdings", tags=["holdings"])


def get_owned_account(account_id: UUID, current_user: User, db: Session) -> Account:
    account = (
        db.query(Account)
        .filter(Account.id == account_id, Account.user_id == current_user.id)
        .first()
    )

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    return account


@router.get("", response_model=list[HoldingResponse])
def list_holdings(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    get_owned_account(account_id, current_user, db)

    transactions = (
        db.query(Transaction, Security)
        .join(Security, Security.id == Transaction.security_id)
        .filter(
            Transaction.account_id == account_id,
            Transaction.deleted_at.is_(None),
        )
        .all()
    )

    holdings: dict[UUID, dict] = {}

    for transaction, security in transactions:
        security_id = security.id

        if security_id not in holdings:
            holdings[security_id] = {
                "security_id": security.id,
                "symbol": security.symbol,
                "company": security.company,
                "shares": Decimal("0"),
                "total_basis": Decimal("0"),
            }

        transaction_type = transaction.type.upper()

        if transaction_type in {"BUY", "DRIP_BUY"}:
            holdings[security_id]["shares"] += transaction.shares or Decimal("0")
            holdings[security_id]["total_basis"] += transaction.cash_amount or Decimal("0")

        elif transaction_type == "SELL":
            holdings[security_id]["shares"] -= transaction.shares or Decimal("0")
            holdings[security_id]["total_basis"] -= transaction.cash_amount or Decimal("0")

    return [
        HoldingResponse(**holding)
        for holding in holdings.values()
        if holding["shares"] != Decimal("0")
    ]
