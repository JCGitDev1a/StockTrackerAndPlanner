from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.core.finance import quantize_money
from app.db.session import get_db
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction_summary import (
    TransactionSummaryResponse,
)

router = APIRouter(
    prefix="/accounts/{account_id}/transactions",
    tags=["transaction-summary"],
)


@router.get("/summary", response_model=TransactionSummaryResponse)
def transaction_summary(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = (
        db.query(Account)
        .filter(
            Account.id == account_id,
            Account.user_id == current_user.id,
        )
        .first()
    )

    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")

    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.account_id == account_id,
            Transaction.deleted_at.is_(None),
        )
        .all()
    )

    buy_count = 0
    sell_count = 0
    dividend_count = 0
    drip_buy_count = 0

    total_buy_amount = Decimal("0")
    total_sell_amount = Decimal("0")
    total_dividend_amount = Decimal("0")

    for transaction in transactions:
        transaction_type = transaction.type.upper()

        if transaction_type == "BUY":
            buy_count += 1
            total_buy_amount += (
                transaction.cash_amount or Decimal("0")
            )

        elif transaction_type == "SELL":
            sell_count += 1
            total_sell_amount += (
                transaction.cash_amount or Decimal("0")
            )

        elif transaction_type == "DIVIDEND":
            dividend_count += 1
            total_dividend_amount += (
                transaction.cash_amount or Decimal("0")
            )

        elif transaction_type == "DRIP_BUY":
            drip_buy_count += 1

    return TransactionSummaryResponse(
        total_transactions=len(transactions),
        buy_count=buy_count,
        sell_count=sell_count,
        dividend_count=dividend_count,
        drip_buy_count=drip_buy_count,
        total_buy_amount=quantize_money(
            total_buy_amount
        ),
        total_sell_amount=quantize_money(
            total_sell_amount
        ),
        total_dividend_amount=quantize_money(
            total_dividend_amount
        ),
    )
