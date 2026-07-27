"""add exchange_rate table

Revision ID: 17131869b9ad
Revises: a4171db90c88
Create Date: 2026-07-27 20:34:32.480700

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17131869b9ad'
down_revision: Union[str, Sequence[str], None] = 'a4171db90c88'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "exchange_rate",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("base_currency", sa.String(length=3), nullable=False),
        sa.Column("target_currency", sa.String(length=3), nullable=False),
        sa.Column("rate", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_exchange_rate_pair_date",
        "exchange_rate",
        ["base_currency", "target_currency", "fetched_at"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_exchange_rate_pair_date", table_name="exchange_rate")
    op.drop_table("exchange_rate")