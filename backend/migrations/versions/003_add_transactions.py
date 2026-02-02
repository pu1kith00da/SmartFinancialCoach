"""Add transactions and categories tables

Revision ID: 003
Revises: 002
Create Date: 2026-01-31 01:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create transactions table
    op.create_table(
        'transactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('plaid_transaction_id', sa.String(length=100), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('authorized_date', sa.Date(), nullable=True),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('merchant_name', sa.String(length=200), nullable=True),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='USD'),
        sa.Column('type', sa.String(length=10), nullable=False),
        sa.Column('status', sa.String(length=10), nullable=False, server_default='posted'),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('category_detailed', sa.String(length=200), nullable=True),
        sa.Column('plaid_category', sa.Text(), nullable=True),
        sa.Column('user_category', sa.String(length=100), nullable=True),
        sa.Column('user_notes', sa.Text(), nullable=True),
        sa.Column('is_excluded', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('location_address', sa.String(length=500), nullable=True),
        sa.Column('location_city', sa.String(length=100), nullable=True),
        sa.Column('location_region', sa.String(length=100), nullable=True),
        sa.Column('location_country', sa.String(length=2), nullable=True),
        sa.Column('payment_channel', sa.String(length=50), nullable=True),
        sa.Column('pending_transaction_id', sa.String(length=100), nullable=True),
        sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('recurring_frequency', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('plaid_transaction_id')
    )
    op.create_index('ix_transactions_account_id', 'transactions', ['account_id'])
    op.create_index('ix_transactions_user_id', 'transactions', ['user_id'])
    op.create_index('ix_transactions_date', 'transactions', ['date'])
    op.create_index('ix_transactions_type', 'transactions', ['type'])
    op.create_index('ix_transactions_category', 'transactions', ['category'])
    
    # Create transaction_categories table
    op.create_table(
        'transaction_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('parent_category', sa.String(length=100), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('monthly_budget', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('keywords', sa.Text(), nullable=True),
        sa.Column('merchant_patterns', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_transaction_categories_user_id', 'transaction_categories', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_transaction_categories_user_id', table_name='transaction_categories')
    op.drop_table('transaction_categories')
    
    op.drop_index('ix_transactions_category', table_name='transactions')
    op.drop_index('ix_transactions_type', table_name='transactions')
    op.drop_index('ix_transactions_date', table_name='transactions')
    op.drop_index('ix_transactions_user_id', table_name='transactions')
    op.drop_index('ix_transactions_account_id', table_name='transactions')
    op.drop_table('transactions')
