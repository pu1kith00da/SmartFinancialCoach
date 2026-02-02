from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, validator
from app.models.subscription import SubscriptionStatus, BillingCycle, DetectionConfidence


class SubscriptionBase(BaseModel):
    """Base schema for subscription with common fields."""
    name: str = Field(..., min_length=1, max_length=200, description="Service name")
    service_provider: str = Field(..., min_length=1, max_length=200, description="Company providing the service")
    category: Optional[str] = Field(None, max_length=100, description="Subscription category")
    amount: float = Field(..., gt=0, description="Billing amount")
    billing_cycle: BillingCycle = Field(..., description="How often billing occurs")
    first_charge_date: date = Field(..., description="Date of first charge")
    description: Optional[str] = Field(None, description="Additional details about subscription")
    website_url: Optional[str] = Field(None, max_length=500, description="Service website")
    
    @validator('amount')
    def validate_amount(cls, v):
        """Validate amount is positive."""
        if v <= 0:
            raise ValueError('Amount must be positive')
        return round(v, 2)


class SubscriptionCreate(SubscriptionBase):
    """Schema for creating a new subscription."""
    is_trial: Optional[bool] = Field(False, description="Whether subscription is in trial period")
    trial_end_date: Optional[date] = Field(None, description="Trial end date")
    cancellation_url: Optional[str] = Field(None, max_length=500, description="URL to cancel subscription")
    
    @validator('trial_end_date')
    def validate_trial_dates(cls, v, values):
        """Validate trial end date is in the future if trial is active."""
        if values.get('is_trial') and v:
            if v <= date.today():
                raise ValueError('Trial end date must be in the future')
        return v


class SubscriptionUpdate(BaseModel):
    """Schema for updating an existing subscription."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    service_provider: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, max_length=100)
    amount: Optional[float] = Field(None, gt=0)
    billing_cycle: Optional[BillingCycle] = Field(None)
    description: Optional[str] = Field(None)
    website_url: Optional[str] = Field(None, max_length=500)
    cancellation_url: Optional[str] = Field(None, max_length=500)
    status: Optional[SubscriptionStatus] = Field(None)
    is_trial: Optional[bool] = Field(None)
    trial_end_date: Optional[date] = Field(None)
    
    @validator('amount')
    def validate_amount(cls, v):
        """Validate amount is positive."""
        if v is not None and v <= 0:
            raise ValueError('Amount must be positive')
        return round(v, 2) if v else v


class SubscriptionResponse(SubscriptionBase):
    """Schema for subscription response."""
    id: UUID = Field(..., description="Unique subscription identifier")
    user_id: UUID = Field(..., description="Owner user ID")
    status: SubscriptionStatus = Field(..., description="Current subscription status")
    next_billing_date: date = Field(..., description="Next billing date")
    last_charge_date: Optional[date] = Field(None, description="Last charge date")
    last_charge_amount: Optional[float] = Field(None, description="Last charge amount")
    total_charges: int = Field(0, description="Total number of charges")
    average_amount: Optional[float] = Field(None, description="Average charge amount")
    is_trial: bool = Field(False, description="Whether subscription is in trial")
    trial_end_date: Optional[date] = Field(None, description="Trial end date")
    cancellation_url: Optional[str] = Field(None, description="URL to cancel subscription")
    detection_confidence: DetectionConfidence = Field(..., description="Auto-detection confidence")
    auto_detected: bool = Field(False, description="Whether auto-detected from transactions")
    confirmed_by_user: bool = Field(False, description="Whether confirmed by user")
    logo_url: Optional[str] = Field(None, description="Service logo URL")
    color: Optional[str] = Field(None, description="Brand color")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    # Calculated properties
    monthly_cost: float = Field(..., description="Monthly cost calculation")
    annual_cost: float = Field(..., description="Annual cost calculation")
    days_until_next_billing: int = Field(..., description="Days until next billing")
    is_trial_expiring_soon: bool = Field(False, description="Whether trial expires within 7 days")
    
    class Config:
        from_attributes = True


class SubscriptionDetectionCreate(BaseModel):
    """Schema for creating subscription from detection."""
    transaction_ids: List[UUID] = Field(..., description="Transaction IDs that form the subscription pattern")
    name: str = Field(..., min_length=1, max_length=200, description="Detected service name")
    service_provider: str = Field(..., min_length=1, max_length=200, description="Detected company name")
    amount: float = Field(..., gt=0, description="Detected billing amount")
    billing_cycle: BillingCycle = Field(..., description="Detected billing cycle")
    confidence: DetectionConfidence = Field(..., description="Detection confidence level")


class SubscriptionDetectionResponse(BaseModel):
    """Schema for subscription detection results."""
    id: UUID = Field(..., description="Detection result ID")
    name: str = Field(..., description="Detected service name")
    service_provider: str = Field(..., description="Detected company name")
    amount: float = Field(..., description="Detected billing amount")
    billing_cycle: BillingCycle = Field(..., description="Detected billing cycle")
    confidence: DetectionConfidence = Field(..., description="Detection confidence")
    transaction_count: int = Field(..., description="Number of matching transactions")
    first_transaction_date: date = Field(..., description="First transaction date")
    last_transaction_date: date = Field(..., description="Last transaction date")
    predicted_next_date: date = Field(..., description="Predicted next charge date")
    average_days_between: float = Field(..., description="Average days between charges")
    amount_variance: float = Field(..., description="Amount variance percentage")
    suggested_category: Optional[str] = Field(None, description="Suggested category")
    
    class Config:
        from_attributes = True


class SubscriptionUsage(BaseModel):
    """Schema for subscription usage tracking."""
    subscription_id: UUID = Field(..., description="Subscription ID")
    month: date = Field(..., description="Usage month (first day of month)")
    usage_amount: Optional[float] = Field(None, description="Usage amount/quantity")
    usage_cost: Optional[float] = Field(None, description="Additional usage cost")
    total_cost: float = Field(..., description="Total cost for the month")
    notes: Optional[str] = Field(None, description="Usage notes")


class SubscriptionStats(BaseModel):
    """Schema for subscription statistics."""
    total_subscriptions: int = Field(..., description="Total number of subscriptions")
    active_subscriptions: int = Field(..., description="Number of active subscriptions")
    cancelled_subscriptions: int = Field(..., description="Number of cancelled subscriptions")
    total_monthly_cost: float = Field(..., description="Total monthly cost")
    total_annual_cost: float = Field(..., description="Total annual cost")
    # most_expensive: Optional["SubscriptionResponse"] = Field(None, description="Most expensive subscription")
    category_breakdown: dict = Field(..., description="Cost breakdown by category")
    # upcoming_renewals: List["SubscriptionResponse"] = Field(..., description="Subscriptions renewing soon")
    # trial_expiring_soon: List["SubscriptionResponse"] = Field(..., description="Trials expiring soon")
    
    class Config:
        from_attributes = True


class SubscriptionBulkAction(BaseModel):
    """Schema for bulk operations on subscriptions."""
    subscription_ids: List[UUID] = Field(..., min_items=1, description="List of subscription IDs")
    action: str = Field(..., description="Action to perform (cancel, pause, resume)")
    reason: Optional[str] = Field(None, description="Reason for bulk action")