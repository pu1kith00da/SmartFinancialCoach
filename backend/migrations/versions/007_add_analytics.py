"""add net worth snapshots table

Revision ID: 007
Revises: 006
Create Date: 2026-01-31 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create net_worth_snapshots table
    op.create_table(
        'net_worth_snapshots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        
        # Net worth components
        sa.Column('total_assets', sa.Numeric(15, 2), nullable=False),
        sa.Column('total_liabilities', sa.Numeric(15, 2), nullable=False),
        sa.Column('net_worth', sa.Numeric(15, 2), nullable=False),
        
        # Asset breakdown
        sa.Column('liquid_assets', sa.Numeric(15, 2), nullable=True),
        sa.Column('investment_assets', sa.Numeric(15, 2), nullable=True),
        sa.Column('fixed_assets', sa.Numeric(15, 2), nullable=True),
        sa.Column('other_assets', sa.Numeric(15, 2), nullable=True),
        
        # Liability breakdown
        sa.Column('credit_card_debt', sa.Numeric(15, 2), nullable=True),
        sa.Column('student_loans', sa.Numeric(15, 2), nullable=True),
        sa.Column('mortgage_debt', sa.Numeric(15, 2), nullable=True),
        sa.Column('auto_loans', sa.Numeric(15, 2), nullable=True),
        sa.Column('other_debt', sa.Numeric(15, 2), nullable=True),
        
        # Metadata
        sa.Column('snapshot_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('breakdown_data', postgresql.JSON, nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
    )
    
    # Create indexes for efficient queries
    op.create_index('ix_net_worth_snapshots_user_id', 'net_worth_snapshots', ['user_id'])
    op.create_index('ix_net_worth_snapshots_snapshot_date', 'net_worth_snapshots', ['snapshot_date'])
    op.create_index('ix_net_worth_snapshots_user_date', 'net_worth_snapshots', ['user_id', 'snapshot_date'])
    op.create_index('ix_net_worth_snapshots_created_at', 'net_worth_snapshots', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_net_worth_snapshots_created_at', table_name='net_worth_snapshots')
    op.drop_index('ix_net_worth_snapshots_user_date', table_name='net_worth_snapshots')
    op.drop_index('ix_net_worth_snapshots_snapshot_date', table_name='net_worth_snapshots')
    op.drop_index('ix_net_worth_snapshots_user_id', table_name='net_worth_snapshots')
    
    # Drop table
    op.drop_table('net_worth_snapshots')
