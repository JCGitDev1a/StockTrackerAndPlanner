import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.base import Base


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    __table_args__ = (
        UniqueConstraint(
            "account_id",
            "snapshot_date",
            name="uq_portfolio_snapshot_account_date",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    market_value: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    cost_basis: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    unrealized_gain_loss: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    monthly_dividend_income: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    annual_dividend_income: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)

    holdings_count: Mapped[int] = mapped_column(nullable=False)
    watchlist_count: Mapped[int] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
