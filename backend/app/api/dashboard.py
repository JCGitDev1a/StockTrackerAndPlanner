from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models.account import Account
from app.models.user import User
from app.schemas.dashboard import PortfolioSummaryResponse
from app.services.dashboard_service import calculate_portfolio_summary

router = APIRouter(
    prefix="/accounts/{account_id}/dashboard",
    tags=["dashboard"],
)


@router.get("/summary", response_model=PortfolioSummaryResponse)
def portfolio_summary(
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

    return calculate_portfolio_summary(
        db=db,
        account_id=account_id,
    )
