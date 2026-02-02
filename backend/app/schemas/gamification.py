"""
Pydantic schemas for gamification features
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class AchievementCategory(str, Enum):
    """Achievement categories"""
    SAVINGS = "savings"
    SPENDING = "spending"
    BUDGETING = "budgeting"
    GOALS = "goals"
    STREAKS = "streaks"
    CONSISTENCY = "consistency"
    MILESTONES = "milestones"


class AchievementTier(str, Enum):
    """Achievement difficulty tiers"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"


class ChallengeType(str, Enum):
    """Challenge types"""
    SAVINGS = "savings"
    SPENDING_LIMIT = "spending_limit"
    NO_SPEND = "no_spend"
    BUDGET_ADHERENCE = "budget_adherence"
    GOAL_PROGRESS = "goal_progress"
    TRANSACTION_TRACKING = "transaction_tracking"


class ChallengeFrequency(str, Enum):
    """Challenge frequency"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ONE_TIME = "one_time"


class ChallengeStatus(str, Enum):
    """Challenge status"""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"


# Achievement Schemas
class AchievementBase(BaseModel):
    """Base achievement schema"""
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    description: str
    category: AchievementCategory
    tier: AchievementTier = AchievementTier.BRONZE
    xp_reward: int = Field(default=0, ge=0)
    icon: Optional[str] = Field(None, max_length=100)
    criteria: Dict[str, Any]
    is_secret: bool = False
    is_repeatable: bool = False


class AchievementCreate(AchievementBase):
    """Create achievement schema"""
    pass


class AchievementResponse(AchievementBase):
    """Achievement response schema"""
    id: str
    sort_order: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserAchievementResponse(BaseModel):
    """User achievement with details"""
    id: str
    user_id: str
    achievement_id: str
    unlocked_at: datetime
    progress: int
    times_completed: int
    extra_data: Optional[Dict[str, Any]] = None
    achievement: AchievementResponse
    
    model_config = ConfigDict(from_attributes=True)


class AchievementsListResponse(BaseModel):
    """List of achievements"""
    achievements: List[AchievementResponse]
    total: int


class UserAchievementsListResponse(BaseModel):
    """List of user achievements"""
    achievements: List[UserAchievementResponse]
    total: int
    total_xp_earned: int
    completion_rate: float


# Streak Schemas
class StreakResponse(BaseModel):
    """Streak response schema"""
    id: str
    user_id: str
    current_streak: int
    longest_streak: int
    last_activity_date: Optional[date]
    streak_start_date: Optional[date]
    total_activity_days: int
    streak_history: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class StreakUpdate(BaseModel):
    """Update streak"""
    activity_type: str = Field(..., description="Type of activity performed")


# Challenge Schemas
class ChallengeBase(BaseModel):
    """Base challenge schema"""
    code: str = Field(..., max_length=50)
    name: str = Field(..., max_length=100)
    description: str
    challenge_type: ChallengeType
    frequency: ChallengeFrequency
    xp_reward: int = Field(default=0, ge=0)
    icon: Optional[str] = Field(None, max_length=100)
    target_value: Optional[int] = None
    duration_days: Optional[int] = None
    criteria: Dict[str, Any]
    difficulty_level: int = Field(default=1, ge=1, le=5)
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class ChallengeCreate(ChallengeBase):
    """Create challenge schema"""
    pass


class ChallengeResponse(ChallengeBase):
    """Challenge response schema"""
    id: str
    is_active: bool
    sort_order: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ChallengesListResponse(BaseModel):
    """List of challenges"""
    challenges: List[ChallengeResponse]
    total: int


class UserChallengeResponse(BaseModel):
    """User challenge with details"""
    id: str
    user_id: str
    challenge_id: str
    status: ChallengeStatus
    progress: int
    target_progress: Optional[int]
    started_at: datetime
    completed_at: Optional[datetime]
    expires_at: Optional[datetime]
    extra_data: Optional[Dict[str, Any]] = None
    challenge: ChallengeResponse
    
    model_config = ConfigDict(from_attributes=True)


class UserChallengesListResponse(BaseModel):
    """List of user challenges"""
    challenges: List[UserChallengeResponse]
    total: int
    active_count: int
    completed_count: int


class ChallengeAccept(BaseModel):
    """Accept a challenge"""
    challenge_id: str


class ChallengeProgressUpdate(BaseModel):
    """Update challenge progress"""
    progress: int = Field(..., ge=0)
    extra_data: Optional[Dict[str, Any]] = None


# XP Schemas
class XPHistoryResponse(BaseModel):
    """XP history entry"""
    id: str
    user_id: str
    xp_amount: int
    source: str
    source_id: Optional[str]
    description: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class XPHistoryListResponse(BaseModel):
    """List of XP history"""
    history: List[XPHistoryResponse]
    total: int
    total_xp: int


class UserLevelResponse(BaseModel):
    """User level and XP info"""
    user_id: str
    level: int
    current_xp: int
    xp_for_next_level: int
    xp_progress_percentage: float
    total_xp_earned: int


class XPGainResponse(BaseModel):
    """XP gain notification"""
    xp_gained: int
    new_total_xp: int
    source: str
    description: Optional[str]
    level_up: bool = False
    new_level: Optional[int] = None


# Gamification Dashboard
class GamificationDashboardResponse(BaseModel):
    """Complete gamification dashboard"""
    user_level: UserLevelResponse
    streak: Optional[StreakResponse]
    active_challenges: List[UserChallengeResponse]
    recent_achievements: List[UserAchievementResponse]
    total_achievements: int
    unlocked_achievements: int
    achievement_completion_rate: float
    total_xp_earned: int
    level_progress: float
    
    
# Leaderboard Schemas
class LeaderboardEntry(BaseModel):
    """Leaderboard entry"""
    rank: int
    user_id: str
    display_name: str
    level: int
    xp: int
    achievements_count: int
    current_streak: int
    profile_picture_url: Optional[str] = None


class LeaderboardResponse(BaseModel):
    """Leaderboard response"""
    entries: List[LeaderboardEntry]
    user_rank: Optional[int] = None
    total_users: int
    leaderboard_type: str = Field(default="global", description="global, friends, or period-based")


# Stats and Analytics
class GamificationStatsResponse(BaseModel):
    """Gamification statistics"""
    total_users_with_achievements: int
    total_achievements_unlocked: int
    total_challenges_completed: int
    average_level: float
    total_xp_distributed: int
    most_popular_achievement: Optional[AchievementResponse]
    most_popular_challenge: Optional[ChallengeResponse]
    highest_streak: int
