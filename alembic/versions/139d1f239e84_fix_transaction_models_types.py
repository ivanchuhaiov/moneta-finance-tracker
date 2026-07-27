"""fix transaction models types

Revision ID: 139d1f239e84
Revises: 321cb4bd8ddd
Create Date: 2026-07-27 17:42:12.159505

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '139d1f239e84'
down_revision: Union[str, Sequence[str], None] = '321cb4bd8ddd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('credit_operation', 'wallet_id', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('credit_operation', 'credit_type_id', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('credit_operation', 'amount', type_=sa.Numeric(12, 2))

    op.alter_column('debit_operation', 'wallet_id', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('debit_operation', 'debit_type_id', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('debit_operation', 'amount', type_=sa.Numeric(12, 2))

    op.alter_column('transaction_history', 'from_wallet_id', type_=sa.Integer(), postgresql_using='from_wallet_id::integer')
    op.alter_column('transaction_history', 'to_wallet_id', type_=sa.Integer(), postgresql_using='to_wallet_id::integer')
    op.alter_column('transaction_history', 'from_amount', type_=sa.Numeric(12, 2))
    op.alter_column('transaction_history', 'to_amount', type_=sa.Numeric(12, 2))
    op.alter_column('transaction_history', 'exchange_rate', type_=sa.Numeric(18, 6))


def downgrade() -> None:
    op.alter_column('transaction_history', 'exchange_rate', type_=sa.Numeric())
    op.alter_column('transaction_history', 'to_amount', type_=sa.Numeric())
    op.alter_column('transaction_history', 'from_amount', type_=sa.Numeric())
    op.alter_column('transaction_history', 'to_wallet_id', type_=sa.Numeric(12, 2), postgresql_using='to_wallet_id::numeric')
    op.alter_column('transaction_history', 'from_wallet_id', type_=sa.Numeric(12, 2), postgresql_using='from_wallet_id::numeric')

    op.alter_column('debit_operation', 'amount', type_=sa.Numeric())
    op.alter_column('debit_operation', 'debit_type_id', existing_type=sa.INTEGER(), nullable=True)
    op.alter_column('debit_operation', 'wallet_id', existing_type=sa.INTEGER(), nullable=True)

    op.alter_column('credit_operation', 'amount', type_=sa.Numeric())
    op.alter_column('credit_operation', 'credit_type_id', existing_type=sa.INTEGER(), nullable=True)
    op.alter_column('credit_operation', 'wallet_id', existing_type=sa.INTEGER(), nullable=True)
