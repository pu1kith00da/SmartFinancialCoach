from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class UserPreferencesUpdate(BaseModel):
    """Schema for updating user preferences."""
    theme: Optional[str] = None
    currency: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    notification_email: Optional[bool] = None
    notification_push: Optional[bool] = None
    notification_insights: Optional[bool] = None
    notification_goals: Optional[bool] = None
    notification_bills: Optional[bool] = None
    budget_alerts: Optional[bool] = None
    weekly_summary: Optional[bool] = None


class UserPreferencesResponse(BaseModel):
    """Schema for user preferences response."""
    user_id: UUID
    theme: str
    currency: str
    language: str
    timezone: str
    notification_email: bool
    notification_push: bool
    notification_insights: bool
    notification_goals: bool
    notification_bills: bool
    budget_alerts: bool
    weekly_summary: bool
    
    class Config:
        from_attributes = True
