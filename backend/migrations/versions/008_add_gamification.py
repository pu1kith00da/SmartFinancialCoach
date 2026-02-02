"""Add gamification tables

Revision ID: 008
Revises: 007
Create Date: 2026-01-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add gamification fields to users table
    op.add_column('users', sa.Column('xp', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('level', sa.Integer(), nullable=False, server_default='1'))
    
    # Create achievements table
    op.create_table(
        'achievements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category', sa.Enum(
            'SAVINGS', 'SPENDING', 'BUDGETING', 'GOALS', 'STREAKS', 'CONSISTENCY', 'MILESTONES',
            name='achievementcategory'
        ), nullable=False),
        sa.Column('tier', sa.Enum(
            'BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'DIAMOND',
            name='achievementtier'
        ), nullable=False),
        sa.Column('xp_reward', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('icon', sa.String(100), nullable=True),
        sa.Column('criteria', postgresql.JSON(), nullable=False),
        sa.Column('is_secret', sa.Boolean(), default=False),
        sa.Column('is_repeatable', sa.Boolean(), default=False),
        sa.Column('sort_order', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow),
    )
    op.create_index('ix_achievements_code', 'achievements', ['code'])
    op.create_index('ix_achievements_category', 'achievements', ['category'])
    
    # Create user_achievements table
    op.create_table(
        'user_achievements',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('achievement_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('achievements.id', ondelete='CASCADE'), nullable=False),
        sa.Column('unlocked_at', sa.DateTime(), default=datetime.utcnow, nullable=False),
        sa.Column('progress', sa.Integer(), default=100),
        sa.Column('times_completed', sa.Integer(), default=1),
        sa.Column('extra_data', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.UniqueConstraint('user_id', 'achievement_id', 'unlocked_at', name='uix_user_achievement_unlock'),
    )
    op.create_index('ix_user_achievements_user_id', 'user_achievements', ['user_id'])
    op.create_index('ix_user_achievements_achievement_id', 'user_achievements', ['achievement_id'])
    op.create_index('ix_user_achievements_unlocked_at', 'user_achievements', ['unlocked_at'])
    
    # Create streaks table
    op.create_table(
        'streaks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('current_streak', sa.Integer(), default=0, nullable=False),
        sa.Column('longest_streak', sa.Integer(), default=0, nullable=False),
        sa.Column('last_activity_date', sa.Date(), nullable=True),
        sa.Column('streak_start_date', sa.Date(), nullable=True),
        sa.Column('total_activity_days', sa.Integer(), default=0, nullable=False),
        sa.Column('streak_history', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow),
    )
    op.create_index('ix_streaks_user_id', 'streaks', ['user_id'], unique=True)
    
    # Create challenges table
    op.create_table(
        'challenges',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('code', sa.String(50), nullable=False, unique=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('challenge_type', sa.Enum(
            'SAVINGS', 'SPENDING_LIMIT', 'NO_SPEND', 'BUDGET_ADHERENCE', 'GOAL_PROGRESS', 'TRANSACTION_TRACKING',
            name='challengetype'
        ), nullable=False),
        sa.Column('frequency', sa.Enum(
            'DAILY', 'WEEKLY', 'MONTHLY', 'ONE_TIME',
            name='challengefrequency'
        ), nullable=False),
        sa.Column('xp_reward', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('icon', sa.String(100), nullable=True),
        sa.Column('target_value', sa.Integer(), nullable=True),
        sa.Column('duration_days', sa.Integer(), nullable=True),
        sa.Column('criteria', postgresql.JSON(), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('difficulty_level', sa.Integer(), default=1),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('sort_order', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow),
    )
    op.create_index('ix_challenges_code', 'challenges', ['code'])
    op.create_index('ix_challenges_type', 'challenges', ['challenge_type'])
    op.create_index('ix_challenges_active', 'challenges', ['is_active'])
    
    # Create user_challenges table
    op.create_table(
        'user_challenges',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('challenge_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('challenges.id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(20), default='active', nullable=False),
        sa.Column('progress', sa.Integer(), default=0, nullable=False),
        sa.Column('target_progress', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(), default=datetime.utcnow, nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('extra_data', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.UniqueConstraint('user_id', 'challenge_id', 'started_at', name='uix_user_challenge'),
    )
    op.create_index('ix_user_challenges_user_id', 'user_challenges', ['user_id'])
    op.create_index('ix_user_challenges_challenge_id', 'user_challenges', ['challenge_id'])
    op.create_index('ix_user_challenges_status', 'user_challenges', ['status'])
    
    # Create xp_history table
    op.create_table(
        'xp_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('xp_amount', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(50), nullable=False),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('description', sa.String(200), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow, nullable=False),
    )
    op.create_index('ix_xp_history_user_id', 'xp_history', ['user_id'])
    op.create_index('ix_xp_history_created_at', 'xp_history', ['created_at'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('ix_xp_history_created_at', table_name='xp_history')
    op.drop_index('ix_xp_history_user_id', table_name='xp_history')
    op.drop_table('xp_history')
    
    op.drop_index('ix_user_challenges_status', table_name='user_challenges')
    op.drop_index('ix_user_challenges_challenge_id', table_name='user_challenges')
    op.drop_index('ix_user_challenges_user_id', table_name='user_challenges')
    op.drop_table('user_challenges')
    
    op.drop_index('ix_challenges_active', table_name='challenges')
    op.drop_index('ix_challenges_type', table_name='challenges')
    op.drop_index('ix_challenges_code', table_name='challenges')
    op.drop_table('challenges')
    
    op.drop_index('ix_streaks_user_id', table_name='streaks')
    op.drop_table('streaks')
    
    op.drop_index('ix_user_achievements_unlocked_at', table_name='user_achievements')
    op.drop_index('ix_user_achievements_achievement_id', table_name='user_achievements')
    op.drop_index('ix_user_achievements_user_id', table_name='user_achievements')
    op.drop_table('user_achievements')
    
    op.drop_index('ix_achievements_category', table_name='achievements')
    op.drop_index('ix_achievements_code', table_name='achievements')
    op.drop_table('achievements')
    
    # Remove gamification fields from users
    op.drop_column('users', 'level')
    op.drop_column('users', 'xp')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS achievementcategory')
    op.execute('DROP TYPE IF EXISTS achievementtier')
    op.execute('DROP TYPE IF EXISTS challengetype')
    op.execute('DROP TYPE IF EXISTS challengefrequency')
