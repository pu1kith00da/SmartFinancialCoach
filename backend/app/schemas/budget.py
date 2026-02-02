"""Budget schemas for API requests and responses."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class BudgetBase(BaseModel):
    """Base budget schema."""
    category: str = Field(..., min_length=1, max_length=100, description="Budget category")
    amount: float = Field(..., gt=0, description="Budget amount")
    period: str = Field(default="monthly", pattern="^(monthly|weekly|yearly)$", description="Budget period")
    is_active: bool = Field(default=True, description="Whether budget is active")
    notes: Optional[str] = Field(None, max_length=1000, description="Optional notes")


class BudgetCreate(BudgetBase):
    """Schema for creating a budget."""
    pass


class BudgetUpdate(BaseModel):
    """Schema for updating a budget."""
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    amount: Optional[float] = Field(None, gt=0)
    period: Optional[str] = Field(None, pattern="^(monthly|weekly|yearly)$")
    is_active: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=1000)


class BudgetResponse(BudgetBase):
    """Schema for budget response."""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    
    # Additional computed fields
    spent: Optional[float] = Field(None, description="Amount spent in current period")
    remaining: Optional[float] = Field(None, description="Amount remaining in budget")
    percentage: Optional[float] = Field(None, description="Percentage of budget used")
    status: Optional[str] = Field(None, description="Budget status: on_track, warning, exceeded")

    class Config:
        from_attributes = True


class BudgetSummaryResponse(BaseModel):
    """Schema for budget summary."""
    category: str
    budgeted: float
    spent: float
    percentage: float
    status: str  # on_track, warning, exceeded


class BudgetListResponse(BaseModel):
    """Schema for list of budgets."""
    budgets: list[BudgetResponse]
    total_budgeted: float
    total_spent: float
    month: str


class BudgetSummaryListResponse(BaseModel):
    """Schema for budget summary list."""
    budgets: list[BudgetSummaryResponse]
    total_budgeted: float
    total_spent: float
    month: str
