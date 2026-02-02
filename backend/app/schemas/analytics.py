"""
Schemas for analytics and reporting endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


# Spending Analytics Schemas

class SpendingByCategory(BaseModel):
    """Spending breakdown by category."""
    category: str
    amount: float
    transaction_count: int
    percentage: float
    average_transaction: float


class SpendingTrend(BaseModel):
    """Spending trend over time."""
    date: date
    amount: float
    transaction_count: int


class SpendingAnalytics(BaseModel):
    """Complete spending analytics."""
    total_spending: float
    period_start: date
    period_end: date
    by_category: List[SpendingByCategory]
    trend_data: List[SpendingTrend]
    top_merchants: List[Dict[str, Any]]
    daily_average: float
    comparison_to_previous_period: Optional[float] = None


# Income Analytics Schemas

class IncomeBySource(BaseModel):
    """Income breakdown by source."""
    source: str
    amount: float
    transaction_count: int
    percentage: float


class IncomeAnalytics(BaseModel):
    """Complete income analytics."""
    total_income: float
    period_start: date
    period_end: date
    by_source: List[IncomeBySource]
    trend_data: List[Dict[str, Any]]
    monthly_average: float
    comparison_to_previous_period: Optional[float] = None


# Cash Flow Schemas

class CashFlowPeriod(BaseModel):
    """Cash flow for a specific period."""
    date: date
    income: float
    expenses: float
    net_cash_flow: float


class CashFlowAnalytics(BaseModel):
    """Complete cash flow analytics."""
    period_start: date
    period_end: date
    total_income: float
    total_expenses: float
    net_cash_flow: float
    periods: List[CashFlowPeriod]
    average_monthly_income: float
    average_monthly_expenses: float
    savings_rate: float  # Percentage


# Net Worth Schemas

class NetWorthSnapshotResponse(BaseModel):
    """Net worth snapshot response."""
    id: UUID
    user_id: UUID
    total_assets: float
    total_liabilities: float
    net_worth: float
    liquid_assets: Optional[float] = None
    investment_assets: Optional[float] = None
    fixed_assets: Optional[float] = None
    other_assets: Optional[float] = None
    credit_card_debt: Optional[float] = None
    student_loans: Optional[float] = None
    mortgage_debt: Optional[float] = None
    auto_loans: Optional[float] = None
    other_debt: Optional[float] = None
    snapshot_date: datetime
    debt_to_asset_ratio: float
    liquid_ratio: float
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NetWorthCreate(BaseModel):
    """Create net worth snapshot."""
    total_assets: float = Field(..., ge=0)
    total_liabilities: float = Field(..., ge=0)
    liquid_assets: Optional[float] = Field(None, ge=0)
    investment_assets: Optional[float] = Field(None, ge=0)
    fixed_assets: Optional[float] = Field(None, ge=0)
    other_assets: Optional[float] = Field(None, ge=0)
    credit_card_debt: Optional[float] = Field(None, ge=0)
    student_loans: Optional[float] = Field(None, ge=0)
    mortgage_debt: Optional[float] = Field(None, ge=0)
    auto_loans: Optional[float] = Field(None, ge=0)
    other_debt: Optional[float] = Field(None, ge=0)
    snapshot_date: Optional[datetime] = None
    notes: Optional[str] = None


class NetWorthHistory(BaseModel):
    """Historical net worth data."""
    snapshots: List[NetWorthSnapshotResponse]
    total_count: int
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    net_worth_change: Optional[float] = None
    percentage_change: Optional[float] = None


# Period Comparison Schemas

class PeriodComparison(BaseModel):
    """Comparison between two periods."""
    current_period: Dict[str, Any]
    previous_period: Dict[str, Any]
    changes: Dict[str, float]  # Absolute changes
    percentage_changes: Dict[str, float]  # Percentage changes


# Dashboard Summary Schema

class DashboardSummary(BaseModel):
    """Summary data for dashboard."""
    current_balance: float
    total_income_this_month: float
    total_spending_this_month: float
    net_cash_flow_this_month: float
    savings_rate: float
    active_budgets_count: int
    over_budget_count: int
    active_goals_count: int
    goals_on_track: int
    net_worth: Optional[float] = None
    net_worth_change: Optional[float] = None
    top_spending_categories: List[SpendingByCategory]
    upcoming_bills_count: int
    upcoming_bills_amount: float
    active_subscriptions_count: int
    monthly_subscription_cost: float
    recent_insights_count: int
    unread_insights_count: int


# Analytics Query Parameters

class AnalyticsFilters(BaseModel):
    """Common filters for analytics queries."""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    category_ids: Optional[List[UUID]] = None
    account_ids: Optional[List[UUID]] = None
    group_by: Optional[str] = Field(None, pattern="^(day|week|month|year)$")
    compare_to_previous: bool = False


# Transaction Summary Schema

class TransactionSummary(BaseModel):
    """Summary of transaction data."""
    total_transactions: int
    total_amount: float
    average_amount: float
    largest_transaction: Optional[float] = None
    smallest_transaction: Optional[float] = None
    most_frequent_merchant: Optional[str] = None
