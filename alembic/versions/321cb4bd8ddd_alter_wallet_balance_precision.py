"""alter wallet balance precision

Revision ID: 321cb4bd8ddd
Revises: 9a4124a0d668
Create Date: 2026-07-06 20:04:23.688686

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '321cb4bd8ddd'
down_revision: Union[str, Sequence[str], None] = '9a4124a0d668'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'wallet',
        'balance',
        existing_type=sa.Numeric(),
        type_=sa.Numeric(precision=12, scale=2),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        'wallet',
        'balance',
        existing_type=sa.Numeric(precision=12, scale=2),
        type_=sa.Numeric(),
        existing_nullable=False,
    )
