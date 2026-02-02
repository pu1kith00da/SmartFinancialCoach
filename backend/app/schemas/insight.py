from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

from app.models.insight import InsightType, InsightPriority


class InsightBase(BaseModel):
    """Base insight schema."""
    type: InsightType
    priority: InsightPriority = InsightPriority.NORMAL
    title: str = Field(..., max_length=200)
    message: str
    action_type: Optional[str] = Field(None, max_length=50)
    action_data: Optional[Dict[str, Any]] = None
    context_data: Optional[Dict[str, Any]] = None
    category: Optional[str] = Field(None, max_length=100)
    amount: Optional[float] = None
    expires_at: Optional[datetime] = None


class InsightCreate(InsightBase):
    """Schema for creating an insight."""
    user_id: UUID


class InsightResponse(InsightBase):
    """Schema for insight response."""
    id: UUID
    user_id: UUID
    is_read: bool
    is_dismissed: bool
    read_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InsightListResponse(BaseModel):
    """Schema for paginated insight list."""
    insights: List[InsightResponse]
    total: int
    limit: int
    offset: int
    has_more: bool


class InsightFilters(BaseModel):
    """Schema for filtering insights."""
    type: Optional[InsightType] = None
    priority: Optional[InsightPriority] = None
    is_read: Optional[bool] = None
    is_dismissed: Optional[bool] = None
    category: Optional[str] = None
    since: Optional[datetime] = None  # Get insights since this date
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class MarkReadRequest(BaseModel):
    """Schema for marking insights as read."""
    insight_ids: List[UUID]


class DailyNudgeResponse(BaseModel):
    """Schema for daily nudge (today's top insight)."""
    insight: Optional[InsightResponse] = None
    has_insight: bool
    message: Optional[str] = None  # Fallback message if no insight available


class InsightAnalytics(BaseModel):
    """Schema for insight analytics and statistics."""
    total_insights: int
    total_read: int
    total_dismissed: int
    read_rate: float  # Percentage
    dismiss_rate: float  # Percentage
    insights_by_type: Dict[str, int]
    insights_by_priority: Dict[str, int]
    recent_insights_count: int  # Last 7 days
    avg_insights_per_week: float


class AnomalyDetectionResponse(BaseModel):
    """Schema for anomaly detection results."""
    anomalies_found: int
    insights_created: int
    insights: List[InsightResponse]
