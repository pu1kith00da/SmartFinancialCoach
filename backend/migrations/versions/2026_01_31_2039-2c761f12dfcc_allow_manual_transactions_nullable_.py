"""allow_manual_transactions_nullable_fields

Revision ID: 2c761f12dfcc
Revises: 008
Create Date: 2026-01-31 20:39:27.559706+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c761f12dfcc'
down_revision: Union[str, None] = '008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make account_id nullable to allow manual transactions
    op.alter_column('transactions', 'account_id',
                    existing_type=sa.UUID(),
                    nullable=True)
    
    # Make plaid_transaction_id nullable to allow manual transactions
    op.alter_column('transactions', 'plaid_transaction_id',
                    existing_type=sa.VARCHAR(length=100),
                    nullable=True)


def downgrade() -> None:
    # Make plaid_transaction_id not nullable
    op.alter_column('transactions', 'plaid_transaction_id',
                    existing_type=sa.VARCHAR(length=100),
                    nullable=False)
    
    # Make account_id not nullable
    op.alter_column('transactions', 'account_id',
                    existing_type=sa.UUID(),
                    nullable=False)
