from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID

from app.models.goal import GoalType, GoalStatus, GoalPriority


class GoalBase(BaseModel):
    """Base goal schema."""
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    type: GoalType
    priority: GoalPriority = GoalPriority.MEDIUM
    target_amount: float = Field(..., gt=0)
    target_date: Optional[date] = None
    image_url: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=7)
    monthly_target: Optional[float] = Field(None, ge=0)
    auto_contribute: bool = False
    auto_contribute_amount: Optional[float] = Field(None, ge=0)
    auto_contribute_day: Optional[int] = Field(None, ge=1, le=31)
    enable_roundup: bool = False
    debt_account_id: Optional[UUID] = None
    interest_rate: Optional[float] = Field(None, ge=0, le=100)


class GoalCreate(GoalBase):
    """Schema for creating a goal."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Emergency Fund",
                "description": "Build 6 months of expenses",
                "type": "savings",
                "priority": "high",
                "target_amount": 15000.0,
                "target_date": "2026-12-31",
                "current_amount": 2500.0,
                "monthly_target": 1000.0,
                "auto_contribute": True,
                "auto_contribute_amount": 250.0,
                "auto_contribute_day": 1
            }
        }
    )
    
    current_amount: float = Field(default=0.0, ge=0, description="Current amount saved toward goal")
    started_at: date = Field(default_factory=date.today, description="Date goal was started")


class GoalUpdate(BaseModel):
    """Schema for updating a goal."""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    status: Optional[GoalStatus] = None
    priority: Optional[GoalPriority] = None
    target_amount: Optional[float] = Field(None, gt=0)
    target_date: Optional[date] = None
    image_url: Optional[str] = Field(None, max_length=500)
    icon: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=7)
    monthly_target: Optional[float] = Field(None, ge=0)
    auto_contribute: Optional[bool] = None
    auto_contribute_amount: Optional[float] = Field(None, ge=0)
    auto_contribute_day: Optional[int] = Field(None, ge=1, le=31)
    enable_roundup: Optional[bool] = None
    debt_account_id: Optional[UUID] = None
    interest_rate: Optional[float] = Field(None, ge=0, le=100)


class GoalResponse(GoalBase):
    """Schema for goal response."""
    id: UUID
    user_id: UUID
    status: GoalStatus
    current_amount: float
    started_at: date
    completed_at: Optional[datetime] = None
    projected_completion_date: Optional[date] = None
    is_on_track: bool
    progress_percentage: float
    remaining_amount: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GoalListResponse(BaseModel):
    """Schema for paginated goal list."""
    goals: List[GoalResponse]
    total: int
    active_count: int
    completed_count: int


class ContributionCreate(BaseModel):
    """Schema for creating a contribution."""
    amount: float = Field(..., gt=0)
    notes: Optional[str] = None
    source: str = Field(default="manual", max_length=50)
    contributed_at: datetime = Field(default_factory=datetime.utcnow)


class ContributionResponse(BaseModel):
    """Schema for contribution response."""
    id: UUID
    goal_id: UUID
    user_id: UUID
    amount: float
    contributed_at: datetime
    notes: Optional[str] = None
    source: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class GoalProgressResponse(BaseModel):
    """Detailed progress analysis for a goal."""
    goal: GoalResponse
    progress_percentage: float
    remaining_amount: float
    days_remaining: Optional[int] = None
    months_remaining: Optional[float] = None
    projected_completion_date: Optional[date] = None
    is_on_track: bool
    required_monthly_contribution: Optional[float] = None
    recent_contributions: List[ContributionResponse]
    total_contributed: float


class FeasibilityAnalysis(BaseModel):
    """AI-powered feasibility analysis for a goal."""
    is_achievable: bool
    confidence_level: str  # high, medium, low
    estimated_completion_date: Optional[date] = None
    required_monthly_savings: float
    current_savings_rate: float
    shortfall_per_month: Optional[float] = None
    recommendations: List[str]
    scenario_if_increase_10_percent: Optional[dict] = None
    scenario_if_reduce_spending: Optional[dict] = None


class GoalSuggestion(BaseModel):
    """AI-generated goal suggestion."""
    suggested_type: GoalType
    suggested_name: str
    suggested_amount: float
    reason: str
    priority: GoalPriority
