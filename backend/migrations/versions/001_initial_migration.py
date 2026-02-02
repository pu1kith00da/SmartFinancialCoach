"""Initial migration - users and preferences

Revision ID: 001
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True, index=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('first_name', sa.String(100), nullable=False),
        sa.Column('last_name', sa.String(100), nullable=False),
        sa.Column('phone_number', sa.String(20), nullable=True),
        sa.Column('profile_picture_url', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('is_verified', sa.Boolean(), default=False, nullable=False),
        sa.Column('mfa_enabled', sa.Boolean(), default=False, nullable=False),
        sa.Column('mfa_secret', sa.String(32), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )
    
    # Create user_preferences table
    op.create_table(
        'user_preferences',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('theme', sa.String(20), default='light', nullable=False),
        sa.Column('currency', sa.String(3), default='USD', nullable=False),
        sa.Column('language', sa.String(10), default='en', nullable=False),
        sa.Column('timezone', sa.String(50), default='UTC', nullable=False),
        sa.Column('notification_email', sa.Boolean(), default=True, nullable=False),
        sa.Column('notification_push', sa.Boolean(), default=True, nullable=False),
        sa.Column('notification_insights', sa.Boolean(), default=True, nullable=False),
        sa.Column('notification_goals', sa.Boolean(), default=True, nullable=False),
        sa.Column('notification_bills', sa.Boolean(), default=True, nullable=False),
        sa.Column('budget_alerts', sa.Boolean(), default=True, nullable=False),
        sa.Column('weekly_summary', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    )


def downgrade() -> None:
    op.drop_table('user_preferences')
    op.drop_table('users')
