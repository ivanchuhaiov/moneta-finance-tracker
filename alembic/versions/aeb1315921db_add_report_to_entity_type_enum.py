"""add report to entity_type enum

Revision ID: aeb1315921db
Revises: 4562c0bb498b
Create Date: 2026-08-06 10:53:58.254660

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'aeb1315921db'
down_revision: Union[str, Sequence[str], None] = '4562c0bb498b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.get_context().autocommit_block():
        op.execute("ALTER TYPE entitytype RENAME TO entity_type")
        op.execute("ALTER TYPE entity_type ADD VALUE 'report'")


def downgrade() -> None:
    """Downgrade schema."""
    # Postgres не поддерживает удаление отдельного значения из enum-типа.
    # Откат потребовал бы пересоздания типа и миграции данных — не делаем.
    pass
