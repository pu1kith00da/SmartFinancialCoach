from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import date, datetime, timedelta
from decimal import Decimal

from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from app.schemas.budget import (
    BudgetCreate,
    BudgetUpdate,
    BudgetResponse,
    BudgetListResponse,
    BudgetSummaryListResponse
)
from app.services.budget_service import BudgetService

router = APIRouter()


@router.get("", response_model=BudgetListResponse)
async def list_budgets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all budgets for the current user with spending data.
    """
    service = BudgetService(db)
    budgets = await service.list_budgets(current_user.id)
    
    # Get spending for each budget
    budget_responses = []
    for budget in budgets:
        budget_with_spending = await service.get_budget_with_spending(
            budget.id,
            current_user.id
        )
        if budget_with_spending:
            budget_responses.append(BudgetResponse(**budget_with_spending))
    
    total_budgeted = sum(b.amount for b in budgets)
    total_spent = sum(b.spent for b in budget_responses if b.spent)
    
    return BudgetListResponse(
        budgets=budget_responses,
        total_budgeted=float(total_budgeted),
        total_spent=float(total_spent or 0),
        month=datetime.utcnow().replace(day=1).isoformat()
    )


@router.get("/summary", response_model=BudgetSummaryListResponse)
async def get_budget_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get budget summary for the current month.
    Returns spending vs budget by category.
    """
    service = BudgetService(db)
    summary = await service.get_budget_summary(current_user.id)
    
    return BudgetSummaryListResponse(**summary)


@router.get("/{budget_id}", response_model=BudgetResponse)
async def get_budget(
    budget_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific budget by ID with spending data.
    """
    service = BudgetService(db)
    budget = await service.get_budget_with_spending(budget_id, current_user.id)
    
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    return BudgetResponse(**budget)


@router.post("", response_model=BudgetResponse, status_code=201)
async def create_budget(
    budget_data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new budget.
    """
    service = BudgetService(db)
    budget = await service.create_budget(current_user.id, budget_data)
    
    # Get budget with spending data
    budget_with_spending = await service.get_budget_with_spending(budget.id, current_user.id)
    
    return BudgetResponse(**budget_with_spending)


@router.put("/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: UUID,
    budget_data: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an existing budget.
    """
    service = BudgetService(db)
    budget = await service.update_budget(budget_id, current_user.id, budget_data)
    
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    # Get budget with spending data
    budget_with_spending = await service.get_budget_with_spending(budget.id, current_user.id)
    
    return BudgetResponse(**budget_with_spending)


@router.delete("/{budget_id}", status_code=204)
async def delete_budget(
    budget_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a budget.
    """
    service = BudgetService(db)
    success = await service.delete_budget(budget_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Budget not found")
    
    return None

