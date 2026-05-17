from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.auth import get_current_user
from app.db.session import get_db
from app.models.account import Account
from app.models.portfolio_snapshot import PortfolioSnapshot
from app.models.user import User
from app.schemas.portfolio_snapshot import (
    PortfolioSnapshotResponse,
)
from app.services.dashboard_service import (
    calculate_portfolio_summary,
)

router = APIRouter(
    prefix="/accounts/{account_id}/snapshots",
    tags=["portfolio-snapshots"],
)


@router.post(
    "/create",
    response_model=PortfolioSnapshotResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_snapshot(
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
        raise HTTPException(
            status_code=404,
            detail="Account not found",
        )

    snapshot_date = date.today()

    existing = (
        db.query(PortfolioSnapshot)
        .filter(
            PortfolioSnapshot.account_id == account_id,
            PortfolioSnapshot.snapshot_date == snapshot_date,
        )
        .first()
    )

    if existing is not None:
        return existing

    summary = calculate_portfolio_summary(
        db=db,
        account_id=account_id,
    )

    snapshot = PortfolioSnapshot(
        account_id=account_id,
        snapshot_date=snapshot_date,

        market_value=summary.total_market_value,
        cost_basis=summary.total_cost_basis,
        unrealized_gain_loss=summary.total_unrealized_gain_loss,

        monthly_dividend_income=summary.monthly_dividend_income,
        annual_dividend_income=summary.annual_dividend_income,

        holdings_count=summary.holdings_count,
        watchlist_count=summary.watchlist_count,
    )

    db.add(snapshot)
    db.commit()
    db.refresh(snapshot)

    return snapshot

@router.get(
    "",
    response_model=list[PortfolioSnapshotResponse],
)
def list_snapshots(
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
        raise HTTPException(
            status_code=404,
            detail="Account not found",
        )

    return (
        db.query(PortfolioSnapshot)
        .filter(
            PortfolioSnapshot.account_id == account_id,
        )
        .order_by(
            PortfolioSnapshot.snapshot_date.desc()
        )
        .all()
    )
