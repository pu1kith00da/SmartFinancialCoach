"""add insights table

Revision ID: 004
Revises: 003
Create Date: 2026-01-31 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create insights table
    op.create_table(
        'insights',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('priority', sa.String(20), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('action_type', sa.String(50), nullable=True),
        sa.Column('action_data', postgresql.JSON, nullable=True),
        sa.Column('context_data', postgresql.JSON, nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('amount', sa.Numeric(15, 2), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_dismissed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('dismissed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    # Create indexes
    op.create_index('ix_insights_user_id', 'insights', ['user_id'])
    op.create_index('ix_insights_type', 'insights', ['type'])
    op.create_index('ix_insights_expires_at', 'insights', ['expires_at'])
    op.create_index('ix_insights_created_at', 'insights', ['created_at'])
    op.create_index('ix_insights_user_read', 'insights', ['user_id', 'is_read'])
    op.create_index('ix_insights_user_dismissed', 'insights', ['user_id', 'is_dismissed'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_insights_user_dismissed', table_name='insights')
    op.drop_index('ix_insights_user_read', table_name='insights')
    op.drop_index('ix_insights_created_at', table_name='insights')
    op.drop_index('ix_insights_expires_at', table_name='insights')
    op.drop_index('ix_insights_type', table_name='insights')
    op.drop_index('ix_insights_user_id', table_name='insights')
    
    # Drop table
    op.drop_table('insights')
