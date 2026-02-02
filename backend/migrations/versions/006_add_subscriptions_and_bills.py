"""Add subscriptions and bills tables

Revision ID: 006
Revises: 005
Create Date: 2026-01-31 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create subscriptions table
    op.create_table('subscriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('service_provider', sa.String(length=200), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('billing_cycle', sa.String(length=20), nullable=False),
        sa.Column('first_charge_date', sa.Date(), nullable=False),
        sa.Column('next_billing_date', sa.Date(), nullable=False),
        sa.Column('last_charge_date', sa.Date(), nullable=True),
        sa.Column('last_charge_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('total_charges', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('average_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('is_trial', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('trial_end_date', sa.Date(), nullable=True),
        sa.Column('cancelled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('website_url', sa.String(length=500), nullable=True),
        sa.Column('cancellation_url', sa.String(length=500), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('detection_confidence', sa.String(length=20), nullable=False, server_default='manual'),
        sa.Column('auto_detected', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('confirmed_by_user', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subscriptions_user_id'), 'subscriptions', ['user_id'], unique=False)
    op.create_index(op.f('ix_subscriptions_next_billing_date'), 'subscriptions', ['next_billing_date'], unique=False)
    op.create_index(op.f('ix_subscriptions_status'), 'subscriptions', ['status'], unique=False)

    # Create bills table
    op.create_table('bills',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('payee', sa.String(length=200), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('estimated_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('min_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('max_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('is_variable_amount', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('frequency', sa.String(length=20), nullable=False),
        sa.Column('first_due_date', sa.Date(), nullable=False),
        sa.Column('next_due_date', sa.Date(), nullable=False),
        sa.Column('last_paid_date', sa.Date(), nullable=True),
        sa.Column('last_paid_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('autopay_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('autopay_account_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reminder_days_before', sa.Integer(), nullable=False, server_default='3'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('auto_detected', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('confirmed_by_user', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('website_url', sa.String(length=500), nullable=True),
        sa.Column('account_number', sa.String(length=100), nullable=True),
        sa.Column('payee_phone', sa.String(length=20), nullable=True),
        sa.Column('payee_email', sa.String(length=255), nullable=True),
        sa.Column('payee_address', sa.Text(), nullable=True),
        sa.Column('logo_url', sa.String(length=500), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bills_user_id'), 'bills', ['user_id'], unique=False)
    op.create_index(op.f('ix_bills_next_due_date'), 'bills', ['next_due_date'], unique=False)
    op.create_index(op.f('ix_bills_status'), 'bills', ['status'], unique=False)

    # Create bill_payments table
    op.create_table('bill_payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bill_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('transaction_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('amount_paid', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('confirmation_number', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='completed'),
        sa.Column('is_late', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bill_payments_bill_id'), 'bill_payments', ['bill_id'], unique=False)
    op.create_index(op.f('ix_bill_payments_user_id'), 'bill_payments', ['user_id'], unique=False)

    # Add foreign key constraints
    op.create_foreign_key('fk_subscriptions_user_id', 'subscriptions', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_bills_user_id', 'bills', 'users', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_bill_payments_bill_id', 'bill_payments', 'bills', ['bill_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_bill_payments_user_id', 'bill_payments', 'users', ['user_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    # Drop foreign key constraints
    op.drop_constraint('fk_bill_payments_user_id', 'bill_payments', type_='foreignkey')
    op.drop_constraint('fk_bill_payments_bill_id', 'bill_payments', type_='foreignkey')
    op.drop_constraint('fk_bills_user_id', 'bills', type_='foreignkey')
    op.drop_constraint('fk_subscriptions_user_id', 'subscriptions', type_='foreignkey')

    # Drop tables
    op.drop_table('bill_payments')
    op.drop_table('bills')
    op.drop_table('subscriptions')