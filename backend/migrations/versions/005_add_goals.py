"""add goals tables

Revision ID: 005
Revises: 004
Create Date: 2024-01-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create goals table
    op.create_table(
        'goals',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('priority', sa.String(20), nullable=False, server_default='medium'),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('target_amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('current_amount', sa.Numeric(15, 2), nullable=False, server_default='0'),
        sa.Column('target_date', sa.Date(), nullable=True),
        sa.Column('started_at', sa.Date(), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('image_url', sa.String(500), nullable=True),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('color', sa.String(7), nullable=True),
        sa.Column('monthly_target', sa.Numeric(15, 2), nullable=True),
        sa.Column('auto_contribute', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('auto_contribute_amount', sa.Numeric(15, 2), nullable=True),
        sa.Column('auto_contribute_day', sa.Integer(), nullable=True),
        sa.Column('enable_roundup', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('debt_account_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('interest_rate', sa.Numeric(5, 2), nullable=True),
        sa.Column('projected_completion_date', sa.Date(), nullable=True),
        sa.Column('is_on_track', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['debt_account_id'], ['accounts.id'], ondelete='SET NULL'),
    )
    
    # Create indexes for goals
    op.create_index('ix_goals_user_id', 'goals', ['user_id'])
    op.create_index('ix_goals_status', 'goals', ['status'])
    op.create_index('ix_goals_type', 'goals', ['type'])
    op.create_index('ix_goals_target_date', 'goals', ['target_date'])
    op.create_index('ix_goals_user_status', 'goals', ['user_id', 'status'])
    
    # Create goal_contributions table
    op.create_table(
        'goal_contributions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('goal_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('contributed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('source', sa.String(50), nullable=False, server_default='manual'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['goal_id'], ['goals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ondelete='SET NULL'),
    )
    
    # Create indexes for goal_contributions
    op.create_index('ix_goal_contributions_goal_id', 'goal_contributions', ['goal_id'])
    op.create_index('ix_goal_contributions_user_id', 'goal_contributions', ['user_id'])
    op.create_index('ix_goal_contributions_contributed_at', 'goal_contributions', ['contributed_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_goal_contributions_contributed_at', table_name='goal_contributions')
    op.drop_index('ix_goal_contributions_user_id', table_name='goal_contributions')
    op.drop_index('ix_goal_contributions_goal_id', table_name='goal_contributions')
    
    # Drop tables
    op.drop_table('goal_contributions')
    
    op.drop_index('ix_goals_user_status', table_name='goals')
    op.drop_index('ix_goals_target_date', table_name='goals')
    op.drop_index('ix_goals_type', table_name='goals')
    op.drop_index('ix_goals_status', table_name='goals')
    op.drop_index('ix_goals_user_id', table_name='goals')
    
    op.drop_table('goals')
