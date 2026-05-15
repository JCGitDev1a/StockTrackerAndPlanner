import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class AccountPosition(Base):
    __tablename__ = "account_positions"

    __table_args__ = (
        UniqueConstraint(
            "account_id",
            "security_id",
            name="uq_account_security",
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

    security_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("securities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    drip_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    recurring_buy_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_watchlist: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    account = relationship("Account")
    security = relationship("Security", back_populates="positions")
