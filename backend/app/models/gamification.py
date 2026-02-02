"""
Gamification models for achievements, challenges, and streaks
"""
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Date, JSON, Enum, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from app.core.database import Base


class AchievementCategory(str, enum.Enum):
    """Achievement categories"""
    SAVINGS = "savings"
    SPENDING = "spending"
    BUDGETING = "budgeting"
    GOALS = "goals"
    STREAKS = "streaks"
    CONSISTENCY = "consistency"
    MILESTONES = "milestones"


class AchievementTier(str, enum.Enum):
    """Achievement difficulty tiers"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


class ChallengeType(str, enum.Enum):
    """Challenge types"""
    SAVINGS = "savings"
    SPENDING_LIMIT = "spending_limit"
    NO_SPEND = "no_spend"
    BUDGET_ADHERENCE = "budget_adherence"
    GOAL_PROGRESS = "goal_progress"
    TRANSACTION_TRACKING = "transaction_tracking"


class ChallengeFrequency(str, enum.Enum):
    """Challenge frequency"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ONE_TIME = "one_time"


class Achievement(Base):
    """Achievement definitions"""
    __tablename__ = "achievements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(Enum(AchievementCategory), nullable=False, index=True)
    tier = Column(Enum(AchievementTier), nullable=False, default=AchievementTier.BRONZE)
    xp_reward = Column(Integer, nullable=False, default=0)
    icon = Column(String(100), nullable=True)  # Icon name or emoji
    criteria = Column(JSON, nullable=False)  # Flexible criteria storage
    is_secret = Column(Boolean, default=False)  # Hidden until unlocked
    is_repeatable = Column(Boolean, default=False)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user_achievements = relationship("UserAchievement", back_populates="achievement", cascade="all, delete-orphan")


class UserAchievement(Base):
    """User's unlocked achievements"""
    __tablename__ = "user_achievements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    achievement_id = Column(UUID(as_uuid=True), ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)
    unlocked_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    progress = Column(Integer, default=100)  # For partial progress tracking
    times_completed = Column(Integer, default=1)  # For repeatable achievements
    extra_data = Column(JSON, nullable=True)  # Additional context (renamed from metadata)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")

    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'achievement_id', 'unlocked_at', name='uix_user_achievement_unlock'),
    )


class Streak(Base):
    """User activity streaks"""
    __tablename__ = "streaks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    last_activity_date = Column(Date, nullable=True)
    streak_start_date = Column(Date, nullable=True)
    total_activity_days = Column(Integer, default=0, nullable=False)
    streak_history = Column(JSON, nullable=True)  # Historical streak data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="streak", uselist=False)


class Challenge(Base):
    """Challenge definitions"""
    __tablename__ = "challenges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    challenge_type = Column(Enum(ChallengeType), nullable=False, index=True)
    frequency = Column(Enum(ChallengeFrequency), nullable=False)
    xp_reward = Column(Integer, nullable=False, default=0)
    icon = Column(String(100), nullable=True)
    target_value = Column(Integer, nullable=True)  # Target amount/count
    duration_days = Column(Integer, nullable=True)  # Challenge duration
    criteria = Column(JSON, nullable=False)  # Flexible criteria
    is_active = Column(Boolean, default=True)
    difficulty_level = Column(Integer, default=1)  # 1-5 scale
    start_date = Column(Date, nullable=True)  # For time-bound challenges
    end_date = Column(Date, nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user_challenges = relationship("UserChallenge", back_populates="challenge", cascade="all, delete-orphan")


class UserChallenge(Base):
    """User's active and completed challenges"""
    __tablename__ = "user_challenges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    challenge_id = Column(UUID(as_uuid=True), ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="active", nullable=False)  # active, completed, failed, abandoned
    progress = Column(Integer, default=0, nullable=False)  # Progress percentage or count
    target_progress = Column(Integer, nullable=True)  # Required progress
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    extra_data = Column(JSON, nullable=True)  # Additional tracking data (renamed from metadata)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="challenges")
    challenge = relationship("Challenge", back_populates="user_challenges")

    # Indexes
    __table_args__ = (
        UniqueConstraint('user_id', 'challenge_id', 'started_at', name='uix_user_challenge'),
    )


class XPHistory(Base):
    """Track XP gains and sources"""
    __tablename__ = "xp_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    xp_amount = Column(Integer, nullable=False)
    source = Column(String(50), nullable=False)  # achievement, challenge, streak, daily_login, etc.
    source_id = Column(UUID(as_uuid=True), nullable=True)  # Reference to achievement/challenge
    description = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="xp_history")
