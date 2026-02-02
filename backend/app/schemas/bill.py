from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, validator
from app.models.bill import BillFrequency, BillStatus, BillCategory


class BillBase(BaseModel):
    """Base schema for bill with common fields."""
    name: str = Field(..., min_length=1, max_length=200, description="Bill name")
    payee: str = Field(..., min_length=1, max_length=200, description="Who to pay")
    category: BillCategory = Field(..., description="Bill category")
    frequency: BillFrequency = Field(..., description="Payment frequency")
    first_due_date: date = Field(..., description="First due date")
    amount: Optional[float] = Field(None, gt=0, description="Fixed bill amount")
    estimated_amount: Optional[float] = Field(None, gt=0, description="Estimated amount for variable bills")
    is_variable_amount: bool = Field(False, description="Whether amount varies")
    description: Optional[str] = Field(None, description="Bill description")
    
    @validator('amount', 'estimated_amount')
    def validate_amounts(cls, v):
        """Validate amounts are positive."""
        if v is not None and v <= 0:
            raise ValueError('Amount must be positive')
        return round(v, 2) if v else v
    
    @validator('first_due_date')
    def validate_first_due_date(cls, v):
        """Validate first due date is not in the past."""
        if v < date.today():
            raise ValueError('First due date cannot be in the past')
        return v


class BillCreate(BillBase):
    """Schema for creating a new bill."""
    account_id: Optional[UUID] = Field(None, description="Account to pay from")
    min_amount: Optional[float] = Field(None, gt=0, description="Minimum amount for variable bills")
    max_amount: Optional[float] = Field(None, gt=0, description="Maximum amount for variable bills")
    autopay_enabled: bool = Field(False, description="Enable autopay")
    autopay_account_id: Optional[UUID] = Field(None, description="Account for autopay")
    reminder_days_before: int = Field(3, ge=0, le=30, description="Days before due date to remind")
    website_url: Optional[str] = Field(None, max_length=500, description="Payee website")
    account_number: Optional[str] = Field(None, max_length=100, description="Account number")
    notes: Optional[str] = Field(None, description="Additional notes")
    
    @validator('max_amount')
    def validate_min_max_amounts(cls, v, values):
        """Validate max amount is greater than min amount."""
        min_amount = values.get('min_amount')
        if v is not None and min_amount is not None and v <= min_amount:
            raise ValueError('Maximum amount must be greater than minimum amount')
        return v


class BillUpdate(BaseModel):
    """Schema for updating an existing bill."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    payee: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[BillCategory] = Field(None)
    frequency: Optional[BillFrequency] = Field(None)
    amount: Optional[float] = Field(None, gt=0)
    estimated_amount: Optional[float] = Field(None, gt=0)
    is_variable_amount: Optional[bool] = Field(None)
    account_id: Optional[UUID] = Field(None)
    min_amount: Optional[float] = Field(None, gt=0)
    max_amount: Optional[float] = Field(None, gt=0)
    autopay_enabled: Optional[bool] = Field(None)
    autopay_account_id: Optional[UUID] = Field(None)
    reminder_days_before: Optional[int] = Field(None, ge=0, le=30)
    status: Optional[BillStatus] = Field(None)
    is_active: Optional[bool] = Field(None)
    description: Optional[str] = Field(None)
    website_url: Optional[str] = Field(None, max_length=500)
    account_number: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None)
    
    @validator('amount', 'estimated_amount', 'min_amount', 'max_amount')
    def validate_amounts(cls, v):
        """Validate amounts are positive."""
        if v is not None and v <= 0:
            raise ValueError('Amount must be positive')
        return round(v, 2) if v else v


class BillResponse(BillBase):
    """Schema for bill response."""
    id: UUID = Field(..., description="Unique bill identifier")
    user_id: UUID = Field(..., description="Owner user ID")
    account_id: Optional[UUID] = Field(None, description="Account to pay from")
    min_amount: Optional[float] = Field(None, description="Minimum amount")
    max_amount: Optional[float] = Field(None, description="Maximum amount")
    next_due_date: date = Field(..., description="Next due date")
    last_paid_date: Optional[date] = Field(None, description="Last payment date")
    last_paid_amount: Optional[float] = Field(None, description="Last payment amount")
    autopay_enabled: bool = Field(False, description="Autopay enabled")
    autopay_account_id: Optional[UUID] = Field(None, description="Autopay account")
    reminder_days_before: int = Field(3, description="Reminder days")
    status: BillStatus = Field(..., description="Current status")
    is_active: bool = Field(True, description="Whether bill is active")
    auto_detected: bool = Field(False, description="Whether auto-detected")
    confirmed_by_user: bool = Field(False, description="Whether confirmed by user")
    website_url: Optional[str] = Field(None, description="Payee website")
    account_number: Optional[str] = Field(None, description="Account number")
    notes: Optional[str] = Field(None, description="Notes")
    logo_url: Optional[str] = Field(None, description="Payee logo")
    color: Optional[str] = Field(None, description="Display color")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    # Calculated properties
    monthly_amount: float = Field(..., description="Monthly cost calculation")
    annual_amount: float = Field(..., description="Annual cost calculation")
    days_until_due: int = Field(..., description="Days until due")
    is_due_soon: bool = Field(False, description="Due within reminder window")
    is_overdue: bool = Field(False, description="Overdue status")
    
    class Config:
        from_attributes = True


class BillPaymentCreate(BaseModel):
    """Schema for creating a bill payment."""
    amount_paid: float = Field(..., gt=0, description="Amount paid")
    payment_date: date = Field(..., description="Payment date")
    payment_method: Optional[str] = Field(None, max_length=50, description="Payment method")
    confirmation_number: Optional[str] = Field(None, max_length=100, description="Confirmation number")
    notes: Optional[str] = Field(None, description="Payment notes")
    transaction_id: Optional[UUID] = Field(None, description="Link to transaction")
    
    @validator('amount_paid')
    def validate_amount_paid(cls, v):
        """Validate payment amount is positive."""
        if v <= 0:
            raise ValueError('Payment amount must be positive')
        return round(v, 2)
    
    @validator('payment_date')
    def validate_payment_date(cls, v):
        """Validate payment date is not in the future."""
        if v > date.today():
            raise ValueError('Payment date cannot be in the future')
        return v


class BillPaymentUpdate(BaseModel):
    """Schema for updating a bill payment."""
    amount_paid: Optional[float] = Field(None, gt=0)
    payment_date: Optional[date] = Field(None)
    payment_method: Optional[str] = Field(None, max_length=50)
    confirmation_number: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = Field(None)
    notes: Optional[str] = Field(None)
    
    @validator('amount_paid')
    def validate_amount_paid(cls, v):
        """Validate payment amount is positive."""
        if v is not None and v <= 0:
            raise ValueError('Payment amount must be positive')
        return round(v, 2) if v else v


class BillPaymentResponse(BaseModel):
    """Schema for bill payment response."""
    id: UUID = Field(..., description="Payment ID")
    bill_id: UUID = Field(..., description="Bill ID")
    user_id: UUID = Field(..., description="User ID")
    transaction_id: Optional[UUID] = Field(None, description="Transaction ID")
    amount_paid: float = Field(..., description="Amount paid")
    payment_date: date = Field(..., description="Payment date")
    due_date: date = Field(..., description="Original due date")
    payment_method: Optional[str] = Field(None, description="Payment method")
    confirmation_number: Optional[str] = Field(None, description="Confirmation number")
    status: str = Field(..., description="Payment status")
    is_late: bool = Field(False, description="Whether payment was late")
    days_late: int = Field(0, description="Days late")
    notes: Optional[str] = Field(None, description="Payment notes")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")
    
    class Config:
        from_attributes = True


class BillStats(BaseModel):
    """Schema for bill statistics."""
    total_bills: int = Field(..., description="Total number of bills")
    active_bills: int = Field(..., description="Number of active bills")
    overdue_bills: int = Field(..., description="Number of overdue bills")
    due_soon_bills: int = Field(..., description="Number of bills due soon")
    total_monthly_amount: float = Field(..., description="Total monthly amount")
    total_annual_amount: float = Field(..., description="Total annual amount")
    category_breakdown: dict = Field(..., description="Amount breakdown by category")
    frequency_breakdown: dict = Field(..., description="Count breakdown by frequency")
    autopay_percentage: float = Field(..., description="Percentage with autopay enabled")
    average_payment_delay: float = Field(..., description="Average days late for payments")
    
    class Config:
        from_attributes = True


class BillDetectionResult(BaseModel):
    """Schema for bill detection results."""
    id: UUID = Field(..., description="Detection result ID")
    name: str = Field(..., description="Detected bill name")
    payee: str = Field(..., description="Detected payee")
    category: BillCategory = Field(..., description="Suggested category")
    frequency: BillFrequency = Field(..., description="Detected frequency")
    amount: float = Field(..., description="Detected amount")
    confidence: float = Field(..., ge=0, le=1, description="Detection confidence (0-1)")
    transaction_count: int = Field(..., description="Number of matching transactions")
    first_transaction_date: date = Field(..., description="First transaction date")
    last_transaction_date: date = Field(..., description="Last transaction date")
    predicted_next_due: date = Field(..., description="Predicted next due date")
    amount_variance: float = Field(..., description="Amount variance percentage")
    
    class Config:
        from_attributes = True


class BillBulkAction(BaseModel):
    """Schema for bulk operations on bills."""
    bill_ids: List[UUID] = Field(..., min_items=1, description="List of bill IDs")
    action: str = Field(..., description="Action to perform (activate, deactivate, delete)")
    reason: Optional[str] = Field(None, description="Reason for bulk action")


class BillReminderSettings(BaseModel):
    """Schema for bill reminder settings."""
    bill_id: UUID = Field(..., description="Bill ID")
    email_enabled: bool = Field(True, description="Email reminders enabled")
    push_enabled: bool = Field(True, description="Push reminders enabled")
    days_before: List[int] = Field([3, 1], description="Days before due date to send reminders")
    custom_message: Optional[str] = Field(None, description="Custom reminder message")
    
    @validator('days_before')
    def validate_days_before(cls, v):
        """Validate reminder days are positive and unique."""
        if not all(day > 0 for day in v):
            raise ValueError('Reminder days must be positive')
        if len(v) != len(set(v)):
            raise ValueError('Reminder days must be unique')
        return sorted(v, reverse=True)