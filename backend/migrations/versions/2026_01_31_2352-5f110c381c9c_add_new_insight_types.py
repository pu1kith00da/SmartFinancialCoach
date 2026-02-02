"""add_new_insight_types

Revision ID: 5f110c381c9c
Revises: 2c761f12dfcc
Create Date: 2026-01-31 23:52:13.828582+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f110c381c9c'
down_revision: Union[str, None] = '2c761f12dfcc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new insight type values to the enum
    op.execute("ALTER TYPE insighttype ADD VALUE IF NOT EXISTS 'budget_alert'")
    op.execute("ALTER TYPE insighttype ADD VALUE IF NOT EXISTS 'goal_behind'")


def downgrade() -> None:
    # Note: PostgreSQL doesn't support removing enum values
    # So we'll leave them in place even on downgrade
    pass
