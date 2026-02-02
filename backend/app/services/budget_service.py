"""Budget service for managing spending limits."""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.budget import Budget
from app.models.transaction import Transaction
from app.schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse, BudgetSummaryResponse


class BudgetService:
    """Service for managing budgets."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_budget(self, user_id: UUID, budget_data: BudgetCreate) -> Budget:
        """Create a new budget."""
        # Check if budget for this category already exists
        existing = await self.db.execute(
            select(Budget).where(
                and_(
                    Budget.user_id == user_id,
                    Budget.category == budget_data.category,
                    Budget.is_active == True
                )
            )
        )
        existing_budget = existing.scalar_one_or_none()
        
        if existing_budget:
            # Deactivate existing budget
            existing_budget.is_active = False
        
        # Create new budget
        budget = Budget(
            user_id=user_id,
            category=budget_data.category,
            amount=budget_data.amount,
            period=budget_data.period,
            is_active=budget_data.is_active,
            notes=budget_data.notes
        )
        
        self.db.add(budget)
        await self.db.commit()
        await self.db.refresh(budget)
        
        return budget
    
    async def get_budget(self, budget_id: UUID, user_id: UUID) -> Optional[Budget]:
        """Get a budget by ID."""
        result = await self.db.execute(
            select(Budget).where(
                and_(
                    Budget.id == budget_id,
                    Budget.user_id == user_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def list_budgets(self, user_id: UUID, include_inactive: bool = False) -> List[Budget]:
        """List all budgets for a user."""
        query = select(Budget).where(Budget.user_id == user_id)
        
        if not include_inactive:
            query = query.where(Budget.is_active == True)
        
        query = query.order_by(Budget.category)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_budget(
        self, 
        budget_id: UUID, 
        user_id: UUID, 
        budget_data: BudgetUpdate
    ) -> Optional[Budget]:
        """Update a budget."""
        budget = await self.get_budget(budget_id, user_id)
        
        if not budget:
            return None
        
        # Update fields
        update_data = budget_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(budget, field, value)
        
        budget.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(budget)
        
        return budget
    
    async def delete_budget(self, budget_id: UUID, user_id: UUID) -> bool:
        """Delete a budget."""
        budget = await self.get_budget(budget_id, user_id)
        
        if not budget:
            return False
        
        await self.db.delete(budget)
        await self.db.commit()
        
        return True
    
    async def get_spending_for_category(
        self,
        user_id: UUID,
        category: str,
        start_date: datetime,
        end_date: datetime
    ) -> Decimal:
        """Get total spending for a category in a date range."""
        result = await self.db.execute(
            select(func.sum(Transaction.amount)).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.user_category == category,
                    Transaction.date >= start_date,
                    Transaction.date <= end_date,
                    Transaction.amount < 0  # Only count expenses (negative amounts)
                )
            )
        )
        total = result.scalar()
        # Return absolute value since transactions are negative
        return abs(total) if total else Decimal(0)
    
    async def get_budget_summary(
        self,
        user_id: UUID,
        month: Optional[datetime] = None
    ) -> dict:
        """Get budget summary with spending for current month."""
        if month is None:
            month = datetime.utcnow()
        
        # Get month date range
        month_start = month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1)
        
        # Get all active budgets
        budgets = await self.list_budgets(user_id, include_inactive=False)
        
        budget_summaries = []
        total_budgeted = 0
        total_spent = 0
        
        for budget in budgets:
            # Get spending for this category
            spent = await self.get_spending_for_category(
                user_id,
                budget.category,
                month_start,
                month_end
            )
            
            spent_float = float(spent)
            budgeted_float = float(budget.amount)
            percentage = (spent_float / budgeted_float * 100) if budgeted_float > 0 else 0
            
            # Determine status
            if percentage >= 100:
                status = "exceeded"
            elif percentage >= 80:
                status = "warning"
            else:
                status = "on_track"
            
            budget_summaries.append(
                BudgetSummaryResponse(
                    category=budget.category,
                    budgeted=budgeted_float,
                    spent=spent_float,
                    percentage=round(percentage, 2),
                    status=status
                )
            )
            
            total_budgeted += budgeted_float
            total_spent += spent_float
        
        return {
            "budgets": budget_summaries,
            "total_budgeted": total_budgeted,
            "total_spent": total_spent,
            "month": month_start.isoformat()
        }
    
    async def get_budget_with_spending(
        self,
        budget_id: UUID,
        user_id: UUID,
        month: Optional[datetime] = None
    ) -> Optional[dict]:
        """Get budget with spending details."""
        budget = await self.get_budget(budget_id, user_id)
        
        if not budget:
            return None
        
        if month is None:
            month = datetime.utcnow()
        
        # Get month date range
        month_start = month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1)
        
        # Get spending
        spent = await self.get_spending_for_category(
            user_id,
            budget.category,
            month_start,
            month_end
        )
        
        spent_float = float(spent)
        budgeted_float = float(budget.amount)
        percentage = (spent_float / budgeted_float * 100) if budgeted_float > 0 else 0
        remaining = budgeted_float - spent_float
        
        # Determine status
        if percentage >= 100:
            status = "exceeded"
        elif percentage >= 80:
            status = "warning"
        else:
            status = "on_track"
        
        return {
            **budget.__dict__,
            "spent": spent_float,
            "remaining": remaining,
            "percentage": round(percentage, 2),
            "status": status
        }
