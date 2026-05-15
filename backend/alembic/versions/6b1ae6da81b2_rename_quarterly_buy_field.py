"""rename quarterly buy field

Revision ID: 6b1ae6da81b2
Revises: 24a3cedff551
Create Date: 2026-05-15 14:17:06.632840

"""

from alembic import op
import sqlalchemy as sa



# revision identifiers, used by Alembic.
revision = '6b1ae6da81b2'
down_revision = '24a3cedff551'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "account_positions",
        "quarterly_buy_enabled",
        new_column_name="recurring_buy_enabled",
    )


def downgrade() -> None:
    op.alter_column(
        "account_positions",
        "recurring_buy_enabled",
        new_column_name="quarterly_buy_enabled",
    )
