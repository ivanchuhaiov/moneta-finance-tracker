"""fix report to entity_type enum

Revision ID: 52c56b445a17
Revises: aeb1315921db
Create Date: 2026-08-06 12:38:49.394941

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '52c56b445a17'
down_revision: Union[str, Sequence[str], None] = 'aeb1315921db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE entity_type ADD VALUE 'REPORT'")


def downgrade() -> None:
    """Downgrade schema."""
    # Postgres не поддерживает удаление отдельного значения из enum-типа.
    # Откат потребовал бы пересоздания типа и миграции данных — не делаем.
    pass
