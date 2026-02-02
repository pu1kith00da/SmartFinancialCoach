from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from enum import Enum


# Enums
class TransactionTypeEnum(str, Enum):
    """Transaction type."""
    DEBIT = "debit"
    CREDIT = "credit"


class TransactionStatusEnum(str, Enum):
    """Transaction status."""
    PENDING = "pending"
    POSTED = "posted"


# Request schemas
class TransactionFilterRequest(BaseModel):
    """Filter parameters for transaction queries."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "category": "Food and Drink",
                "start_date": "2026-01-01",
                "end_date": "2026-01-31",
                "min_amount": 10.0,
                "max_amount": 500.0,
                "type": "debit",
                "limit": 50
            }
        }
    )
    
    account_ids: Optional[List[UUID]] = Field(None, description="Filter by specific account IDs")
    category: Optional[str] = Field(None, description="Filter by transaction category", examples=["Food and Drink"])
    start_date: Optional[date] = Field(None, description="Start date for date range filter", examples=["2026-01-01"])
    end_date: Optional[date] = Field(None, description="End date for date range filter", examples=["2026-01-31"])
    min_amount: Optional[float] = Field(None, description="Minimum transaction amount", examples=[10.0])
    max_amount: Optional[float] = Field(None, description="Maximum transaction amount", examples=[500.0])
    search: Optional[str] = Field(None, description="Search in transaction names and descriptions", examples=["starbucks"])
    type: Optional[TransactionTypeEnum] = Field(None, description="Filter by transaction type (debit/credit)")
    status: Optional[TransactionStatusEnum] = Field(None, description="Filter by transaction status (pending/posted)")
    is_recurring: Optional[bool] = Field(None, description="Filter recurring transactions")
    is_excluded: Optional[bool] = Field(False, description="Include excluded transactions")
    limit: int = Field(default=100, le=500, description="Maximum number of results to return")
    offset: int = Field(default=0, ge=0, description="Number of results to skip for pagination")


class TransactionCreateRequest(BaseModel):
    """Create manual transaction for cash or non-Plaid accounts only."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Coffee with cash",
                "amount": -4.50,
                "category": "Food & Dining",
                "transaction_date": "2026-01-31",
                "transaction_type": "cash",
                "notes": "Cash payment at local cafe"
            }
        }
    )
    
    name: str = Field(..., description="Transaction description", min_length=1, max_length=200)
    amount: float = Field(..., description="Transaction amount (negative for expense, positive for income)")
    category: str = Field(..., description="Transaction category", min_length=1)
    transaction_date: date = Field(..., description="Transaction date")
    transaction_type: str = Field("cash", description="Type: 'cash' or 'planned'", pattern="^(cash|planned)$")
    notes: Optional[str] = Field(None, description="Additional notes (required for manual transactions)", max_length=500)


class TransactionUpdateRequest(BaseModel):
    """Update transaction details."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_category": "Groceries",
                "user_notes": "Weekly grocery shopping",
                "is_excluded": False
            }
        }
    )
    
    user_category: Optional[str] = Field(None, description="Custom category assigned by user", examples=["Groceries"])
    user_notes: Optional[str] = Field(None, description="User notes about the transaction", examples=["Weekly grocery shopping"])
    is_excluded: Optional[bool] = Field(None, description="Exclude from budget calculations")


class BulkCategorizeRequest(BaseModel):
    """Bulk categorize transactions."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "transaction_ids": ["550e8400-e29b-41d4-a716-446655440000"],
                "category": "Groceries"
            }
        }
    )
    
    transaction_ids: List[UUID] = Field(..., description="List of transaction IDs to categorize")
    category: str = Field(..., description="Category to assign to all transactions", examples=["Groceries"])


class TransactionSyncRequest(BaseModel):
    """Request to sync transactions for accounts."""
    account_ids: Optional[List[UUID]] = None  # If None, sync all accounts


# Response schemas
class TransactionResponse(BaseModel):
    """Transaction details."""
    id: UUID
    account_id: Optional[UUID] = None  # Nullable for manual transactions
    date: date
    authorized_date: Optional[date] = None
    name: str
    merchant_name: Optional[str] = None
    amount: float
    currency: str
    type: TransactionTypeEnum
    status: TransactionStatusEnum
    category: Optional[str] = None
    category_detailed: Optional[str] = None
    user_category: Optional[str] = None
    user_notes: Optional[str] = None
    is_excluded: bool
    location_city: Optional[str] = None
    payment_channel: Optional[str] = None
    is_recurring: bool
    recurring_frequency: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """List of transactions with pagination."""
    transactions: List[TransactionResponse]
    total: int
    limit: int
    offset: int
    has_more: bool


class TransactionStatsResponse(BaseModel):
    """Transaction statistics."""
    total_count: int
    total_income: float
    total_expenses: float
    net_amount: float
    average_transaction: float
    categories_breakdown: dict  # {category: amount}
    monthly_trend: dict  # {month: {income, expenses, net}}


class CategorySpending(BaseModel):
    """Spending by category."""
    category: str
    amount: float
    count: int
    percentage: float


class TransactionSyncResponse(BaseModel):
    """Response after syncing transactions."""
    accounts_synced: int
    transactions_added: int
    transactions_updated: int
    last_synced_at: datetime
    success: bool
    message: Optional[str] = None


# Category schemas
class TransactionCategoryRequest(BaseModel):
    """Create/update custom category."""
    name: str = Field(..., min_length=1, max_length=100)
    parent_category: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    monthly_budget: Optional[float] = Field(None, ge=0)
    keywords: Optional[List[str]] = None
    merchant_patterns: Optional[List[str]] = None


class TransactionCategoryResponse(BaseModel):
    """Custom category details."""
    id: UUID
    name: str
    parent_category: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    monthly_budget: Optional[float] = None
    keywords: Optional[List[str]] = None
    merchant_patterns: Optional[List[str]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    """List of custom categories."""
    categories: List[TransactionCategoryResponse]
    total: int
