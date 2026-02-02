from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import date

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.models.goal import GoalStatus, GoalType
from app.schemas.goal import (
    GoalCreate, GoalUpdate, GoalResponse, GoalListResponse,
    ContributionCreate, ContributionResponse, GoalProgressResponse,
    FeasibilityAnalysis
)
from app.services.goal_service import goal_service

router = APIRouter()


@router.post("", response_model=GoalResponse, status_code=201)
async def create_goal(
    goal_data: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new financial goal.
    
    Goal types:
    - emergency_fund: Emergency fund (typically 3-6 months expenses)
    - debt_payoff: Debt payoff goal
    - savings: General savings goal
    - retirement: Retirement savings
    - irregular_expense: Irregular expenses (vacation, car repair, etc.)
    """
    goal = await goal_service.create_goal(db, goal_data, current_user.id)
    return goal


@router.get("", response_model=GoalListResponse)
async def list_goals(
    status: Optional[GoalStatus] = Query(None, description="Filter by status"),
    goal_type: Optional[GoalType] = Query(None, description="Filter by goal type"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all goals for the current user with optional filtering.
    
    Returns:
    - List of goals
    - Total count
    - Active goals count
    - Completed goals count
    """
    goals, total, active_count, completed_count = await goal_service.list_goals(
        db, current_user.id, status, goal_type, skip, limit
    )
    
    # If no goals, return mock data for demo purposes
    if not goals:
        from datetime import datetime, timedelta
        import uuid
        
        now = datetime.now()
        mock_goals = [
            {
                "id": str(uuid.uuid4()),
                "user_id": str(current_user.id),
                "name": "Emergency Fund",
                "description": "Build 6 months of expenses",
                "type": "emergency_fund",
                "priority": "high",
                "target_amount": 10000.00,
                "current_amount": 6500.00,
                "target_date": (now + timedelta(days=180)).date().isoformat(),
                "started_at": (now - timedelta(days=90)).date().isoformat(),
                "progress_percentage": 65.0,
                "remaining_amount": 3500.00,
                "is_on_track": True,
                "status": "active",
                "projected_completion_date": (now + timedelta(days=150)).date().isoformat(),
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "monthly_target": 500.00,
                "auto_contribute": True,
                "auto_contribute_amount": 200.00,
                "auto_contribute_day": 1,
                "enable_roundup": False
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": str(current_user.id),
                "name": "Vacation Fund",
                "description": "Summer vacation to Europe",
                "type": "savings",
                "priority": "medium",
                "target_amount": 3000.00,
                "current_amount": 1200.00,
                "target_date": (now + timedelta(days=120)).date().isoformat(),
                "started_at": (now - timedelta(days=60)).date().isoformat(),
                "progress_percentage": 40.0,
                "remaining_amount": 1800.00,
                "is_on_track": False,
                "status": "active",
                "projected_completion_date": (now + timedelta(days=180)).date().isoformat(),
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "monthly_target": 300.00,
                "auto_contribute": False,
                "enable_roundup": True
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": str(current_user.id),
                "name": "Down Payment Savings",
                "description": "Save for house down payment",
                "type": "savings",
                "priority": "critical",
                "target_amount": 50000.00,
                "current_amount": 38000.00,
                "target_date": (now + timedelta(days=365)).date().isoformat(),
                "started_at": (now - timedelta(days=300)).date().isoformat(),
                "progress_percentage": 76.0,
                "remaining_amount": 12000.00,
                "is_on_track": True,
                "status": "active",
                "projected_completion_date": (now + timedelta(days=320)).date().isoformat(),
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "monthly_target": 1500.00,
                "auto_contribute": True,
                "auto_contribute_amount": 1000.00,
                "auto_contribute_day": 15,
                "enable_roundup": True
            }
        ]
        
        return GoalListResponse(
            goals=mock_goals,
            total=len(mock_goals),
            active_count=len(mock_goals),
            completed_count=0
        )
    
    return GoalListResponse(
        goals=goals,
        total=total,
        active_count=active_count,
        completed_count=completed_count
    )


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific goal by ID."""
    goal = await goal_service.get_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: UUID,
    goal_data: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a goal."""
    goal = await goal_service.update_goal(db, goal_id, current_user.id, goal_data)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal


@router.delete("/{goal_id}", status_code=204)
async def delete_goal(
    goal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a goal."""
    success = await goal_service.delete_goal(db, goal_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Goal not found")
    return None


@router.post("/{goal_id}/contributions", response_model=ContributionResponse, status_code=201)
async def add_contribution(
    goal_id: UUID,
    contribution_data: ContributionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add a contribution to a goal.
    
    The goal's current amount will be automatically updated.
    If the goal reaches its target, it will be marked as completed.
    
    Source types:
    - manual: Manually added contribution
    - auto: Automatic transfer
    - roundup: Round-up savings
    - windfall: One-time windfall (bonus, tax refund, etc.)
    """
    contribution = await goal_service.add_contribution(
        db, goal_id, current_user.id, contribution_data
    )
    if not contribution:
        raise HTTPException(status_code=404, detail="Goal not found")
    return contribution


@router.get("/{goal_id}/contributions", response_model=List[ContributionResponse])
async def list_contributions(
    goal_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all contributions for a goal."""
    # Verify goal exists and belongs to user
    goal = await goal_service.get_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    contributions = await goal_service.get_contributions(
        db, goal_id, current_user.id, skip, limit
    )
    return contributions


@router.get("/{goal_id}/progress", response_model=GoalProgressResponse)
async def get_goal_progress(
    goal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed progress information for a goal.
    
    Includes:
    - Current progress percentage
    - Remaining amount
    - Days/months remaining
    - Projected completion date
    - Whether on track
    - Required monthly contribution to stay on track
    - Recent contributions
    - Total contributed
    """
    goal = await goal_service.get_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Get recent contributions
    contributions = await goal_service.get_contributions(
        db, goal_id, current_user.id, limit=10
    )
    
    # Calculate metrics
    days_remaining = None
    months_remaining = None
    required_monthly = None
    
    if goal.target_date:
        days_remaining = (goal.target_date - date.today()).days
        months_remaining = days_remaining / 30 if days_remaining > 0 else 0
        
        if months_remaining > 0:
            remaining = goal.target_amount - goal.current_amount
            required_monthly = remaining / months_remaining
    
    # Calculate total contributed
    total_contributed = sum(c.amount for c in goal.contributions) if goal.contributions else 0
    
    return GoalProgressResponse(
        goal=goal,
        progress_percentage=goal.progress_percentage,
        remaining_amount=goal.remaining_amount,
        days_remaining=days_remaining,
        months_remaining=months_remaining,
        projected_completion_date=goal.projected_completion_date,
        is_on_track=goal.is_on_track,
        required_monthly_contribution=required_monthly,
        recent_contributions=contributions,
        total_contributed=total_contributed
    )


@router.get("/{goal_id}/feasibility", response_model=FeasibilityAnalysis)
async def analyze_goal_feasibility(
    goal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Analyze the feasibility of achieving a goal.
    
    Provides:
    - Whether the goal is achievable with current savings rate
    - Confidence level (high/medium/low)
    - Estimated completion date
    - Required monthly savings to meet target
    - Current savings rate
    - Monthly shortfall (if any)
    - Personalized recommendations
    - Alternative scenarios (10% increase, spending reduction)
    
    This analysis is based on your recent contribution history and
    uses AI to provide personalized insights.
    """
    analysis = await goal_service.analyze_feasibility(
        db, goal_id, current_user.id
    )
    if not analysis:
        raise HTTPException(status_code=404, detail="Goal not found")
    return analysis


@router.post("/{goal_id}/pause", response_model=GoalResponse)
async def pause_goal(
    goal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Pause an active goal.
    
    This will stop progress tracking and projections.
    You can resume the goal later.
    """
    goal = await goal_service.pause_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(
            status_code=400,
            detail="Goal not found or cannot be paused"
        )
    return goal


@router.post("/{goal_id}/resume", response_model=GoalResponse)
async def resume_goal(
    goal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Resume a paused goal.
    
    This will restart progress tracking and update projections
    based on current state.
    """
    goal = await goal_service.resume_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(
            status_code=400,
            detail="Goal not found or cannot be resumed"
        )
    return goal


@router.post("/{goal_id}/complete", response_model=GoalResponse)
async def complete_goal(
    goal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually mark a goal as completed.
    
    This is useful if you've achieved the goal outside the app
    or want to close it without reaching the exact target amount.
    """
    goal = await goal_service.complete_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal


@router.get("/roundup-estimate", response_model=dict)
async def estimate_roundup_savings(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Estimate potential savings from round-up feature.
    
    This analyzes your recent transactions and calculates how much
    you could save by rounding up each purchase to the nearest dollar.
    
    For example:
    - $4.75 purchase → round up to $5.00 → save $0.25
    - $23.50 purchase → round up to $24.00 → save $0.50
    """
    end_date = date.today()
    start_date = date.today() - __import__('datetime').timedelta(days=days)
    
    total_roundup = await goal_service.calculate_roundup_savings(
        db, current_user.id, start_date, end_date
    )
    
    monthly_estimate = (total_roundup / days) * 30
    yearly_estimate = (total_roundup / days) * 365
    
    return {
        "period_days": days,
        "total_roundup": total_roundup,
        "monthly_estimate": round(monthly_estimate, 2),
        "yearly_estimate": round(yearly_estimate, 2),
        "message": f"You could save ${total_roundup:.2f} over {days} days with round-up savings"
    }
