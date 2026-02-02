"""
API endpoints for analytics and reporting.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
from datetime import date, datetime, timedelta

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.analytics import (
    SpendingAnalytics,
    IncomeAnalytics,
    CashFlowAnalytics,
    NetWorthSnapshotResponse,
    NetWorthCreate,
    NetWorthHistory,
    DashboardSummary
)
from app.services.analytics_service import AnalyticsService

router = APIRouter()


@router.get("/dashboard", response_model=DashboardSummary)
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive dashboard summary with all key metrics.
    
    Includes:
    - Current balance
    - Income and spending for current month
    - Savings rate
    - Budget status
    - Goal progress
    - Net worth
    - Upcoming bills
    - Active subscriptions
    - Recent insights
    """
    service = AnalyticsService(db)
    summary = await service.get_dashboard_summary(current_user.id)
    return summary


@router.get("/spending", response_model=SpendingAnalytics)
async def get_spending_analytics(
    start_date: Optional[date] = Query(None, description="Start date for analysis"),
    end_date: Optional[date] = Query(None, description="End date for analysis"),
    compare: bool = Query(False, description="Compare with previous period"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed spending analytics for a period.
    
    Query parameters:
    - start_date: Start of period (default: beginning of current month)
    - end_date: End of period (default: today)
    - compare: Compare with previous period (default: false)
    
    Returns:
    - Total spending
    - Spending by category
    - Daily trends
    - Top merchants
    - Comparison to previous period (if requested)
    """
    # Default to current month if not specified
    if not start_date:
        now = datetime.utcnow()
        start_date = now.replace(day=1).date()
    if not end_date:
        end_date = datetime.utcnow().date()
    
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date"
        )
    
    service = AnalyticsService(db)
    analytics = await service.get_spending_analytics(
        current_user.id,
        start_date,
        end_date,
        compare
    )
    return analytics


@router.get("/income", response_model=IncomeAnalytics)
async def get_income_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    compare: bool = Query(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed income analytics for a period.
    
    Returns:
    - Total income
    - Income by source
    - Trends over time
    - Monthly average
    - Comparison to previous period (if requested)
    """
    # Default to current month
    if not start_date:
        now = datetime.utcnow()
        start_date = now.replace(day=1).date()
    if not end_date:
        end_date = datetime.utcnow().date()
    
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date"
        )
    
    service = AnalyticsService(db)
    analytics = await service.get_income_analytics(
        current_user.id,
        start_date,
        end_date,
        compare
    )
    return analytics


@router.get("/cash-flow", response_model=CashFlowAnalytics)
async def get_cash_flow_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get cash flow analytics (income vs expenses).
    
    Returns:
    - Total income and expenses
    - Net cash flow
    - Daily breakdown
    - Averages
    - Savings rate
    """
    # Default to current month
    if not start_date:
        now = datetime.utcnow()
        start_date = now.replace(day=1).date()
    if not end_date:
        end_date = datetime.utcnow().date()
    
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date"
        )
    
    service = AnalyticsService(db)
    analytics = await service.get_cash_flow_analytics(
        current_user.id,
        start_date,
        end_date
    )
    return analytics


@router.get("/net-worth", response_model=NetWorthHistory)
async def get_net_worth_history(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get historical net worth data.
    
    Query parameters:
    - start_date: Filter snapshots from this date
    - end_date: Filter snapshots to this date
    - limit: Maximum number of snapshots (default: 100, max: 500)
    
    Returns:
    - Historical snapshots
    - Net worth change over period
    - Percentage change
    """
    service = AnalyticsService(db)
    history = await service.get_net_worth_history(
        current_user.id,
        start_date,
        end_date,
        limit
    )
    return NetWorthHistory(**history)


@router.post("/net-worth", response_model=NetWorthSnapshotResponse, status_code=status.HTTP_201_CREATED)
async def create_net_worth_snapshot(
    data: NetWorthCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new net worth snapshot.
    
    Manually record your net worth at a point in time.
    Include breakdown of assets and liabilities for detailed tracking.
    """
    service = AnalyticsService(db)
    snapshot = await service.create_net_worth_snapshot(current_user.id, data)
    return NetWorthSnapshotResponse.model_validate(snapshot)


@router.get("/net-worth/latest", response_model=Optional[NetWorthSnapshotResponse])
async def get_latest_net_worth(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the most recent net worth snapshot."""
    service = AnalyticsService(db)
    history = await service.get_net_worth_history(current_user.id, limit=1)
    
    if history["snapshots"]:
        return NetWorthSnapshotResponse.model_validate(history["snapshots"][0])
    return None


@router.get("/trends/spending")
async def get_spending_trends(
    months: int = Query(6, ge=1, le=24, description="Number of months to analyze"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get spending trends over multiple months.
    
    Useful for visualizing long-term spending patterns.
    """
    service = AnalyticsService(db)
    end_date = datetime.utcnow().date()
    
    trends = []
    for i in range(months):
        # Calculate month boundaries
        month_end = end_date.replace(day=1) - timedelta(days=i*30)
        month_start = (month_end - timedelta(days=30)).replace(day=1)
        
        analytics = await service.get_spending_analytics(
            current_user.id,
            month_start,
            month_end
        )
        
        trends.append({
            "month": month_start.strftime("%Y-%m"),
            "total": analytics.total_spending,
            "by_category": [
                {"category": c.category, "amount": c.amount}
                for c in analytics.by_category
            ]
        })
    
    return {"trends": trends}


@router.get("/comparison")
async def compare_periods(
    period_type: str = Query("month", pattern="^(week|month|quarter|year)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Compare current period with previous period.
    
    Period types: week, month, quarter, year
    
    Returns side-by-side comparison of key metrics.
    """
    service = AnalyticsService(db)
    now = datetime.utcnow()
    
    # Calculate period boundaries
    if period_type == "week":
        current_start = (now - timedelta(days=now.weekday())).date()
        current_end = current_start + timedelta(days=6)
        previous_start = current_start - timedelta(days=7)
        previous_end = current_start - timedelta(days=1)
    elif period_type == "month":
        current_start = now.replace(day=1).date()
        current_end = now.date()
        previous_end = current_start - timedelta(days=1)
        previous_start = previous_end.replace(day=1)
    elif period_type == "quarter":
        quarter = (now.month - 1) // 3
        current_start = now.replace(month=quarter*3 + 1, day=1).date()
        current_end = now.date()
        previous_start = (current_start - timedelta(days=90)).replace(day=1)
        previous_end = current_start - timedelta(days=1)
    else:  # year
        current_start = now.replace(month=1, day=1).date()
        current_end = now.date()
        previous_start = current_start.replace(year=current_start.year - 1)
        previous_end = current_start - timedelta(days=1)
    
    # Get analytics for both periods
    current_spending = await service.get_spending_analytics(
        current_user.id, current_start, current_end
    )
    previous_spending = await service.get_spending_analytics(
        current_user.id, previous_start, previous_end
    )
    
    current_income = await service.get_income_analytics(
        current_user.id, current_start, current_end
    )
    previous_income = await service.get_income_analytics(
        current_user.id, previous_start, previous_end
    )
    
    return {
        "period_type": period_type,
        "current": {
            "start": current_start,
            "end": current_end,
            "spending": current_spending.total_spending,
            "income": current_income.total_income,
            "net": current_income.total_income - current_spending.total_spending
        },
        "previous": {
            "start": previous_start,
            "end": previous_end,
            "spending": previous_spending.total_spending,
            "income": previous_income.total_income,
            "net": previous_income.total_income - previous_spending.total_spending
        },
        "changes": {
            "spending": current_spending.total_spending - previous_spending.total_spending,
            "income": current_income.total_income - previous_income.total_income,
            "net": (current_income.total_income - current_spending.total_spending) - 
                   (previous_income.total_income - previous_spending.total_spending)
        }
    }
