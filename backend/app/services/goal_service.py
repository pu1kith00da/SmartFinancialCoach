from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from uuid import UUID
from decimal import Decimal
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.goal import Goal, GoalContribution, GoalStatus, GoalType
from app.models.transaction import Transaction
from app.schemas.goal import (
    GoalCreate, GoalUpdate, ContributionCreate,
    FeasibilityAnalysis, GoalSuggestion
)


class GoalService:
    """Service for managing financial goals."""
    
    async def create_goal(
        self,
        db: AsyncSession,
        goal_data: GoalCreate,
        user_id: UUID
    ) -> Goal:
        """Create a new financial goal."""
        goal = Goal(
            user_id=user_id,
            **goal_data.model_dump()
        )
        
        # Calculate initial projection
        if goal.target_date and goal.target_amount > 0:
            await self._update_goal_projection(db, goal, user_id)
        
        db.add(goal)
        await db.commit()
        await db.refresh(goal)
        return goal
    
    async def get_goal(
        self,
        db: AsyncSession,
        goal_id: UUID,
        user_id: UUID
    ) -> Optional[Goal]:
        """Get a goal by ID."""
        result = await db.execute(
            select(Goal)
            .options(selectinload(Goal.contributions))
            .where(and_(Goal.id == goal_id, Goal.user_id == user_id))
        )
        return result.scalar_one_or_none()
    
    async def list_goals(
        self,
        db: AsyncSession,
        user_id: UUID,
        status: Optional[GoalStatus] = None,
        goal_type: Optional[GoalType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Goal], int, int, int]:
        """
        List goals with optional filtering.
        Returns: (goals, total_count, active_count, completed_count)
        """
        # Base query
        query = select(Goal).where(Goal.user_id == user_id)
        
        # Apply filters
        if status:
            query = query.where(Goal.status == status)
        if goal_type:
            query = query.where(Goal.type == goal_type)
        
        # Order by priority and created date
        query = query.order_by(
            Goal.priority.desc(),
            Goal.created_at.desc()
        )
        
        # Get total count
        total_count = await db.scalar(
            select(func.count()).select_from(query.subquery())
        )
        
        # Get active count
        active_count = await db.scalar(
            select(func.count())
            .select_from(Goal)
            .where(and_(Goal.user_id == user_id, Goal.status == GoalStatus.ACTIVE))
        )
        
        # Get completed count
        completed_count = await db.scalar(
            select(func.count())
            .select_from(Goal)
            .where(and_(Goal.user_id == user_id, Goal.status == GoalStatus.COMPLETED))
        )
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        goals = list(result.scalars().all())
        
        return goals, total_count or 0, active_count or 0, completed_count or 0
    
    async def update_goal(
        self,
        db: AsyncSession,
        goal_id: UUID,
        user_id: UUID,
        goal_data: GoalUpdate
    ) -> Optional[Goal]:
        """Update a goal."""
        goal = await self.get_goal(db, goal_id, user_id)
        if not goal:
            return None
        
        # Update fields
        update_data = goal_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(goal, field, value)
        
        # Recalculate projection if target changed
        if 'target_amount' in update_data or 'target_date' in update_data:
            await self._update_goal_projection(db, goal, user_id)
        
        await db.commit()
        await db.refresh(goal)
        return goal
    
    async def delete_goal(
        self,
        db: AsyncSession,
        goal_id: UUID,
        user_id: UUID
    ) -> bool:
        """Delete a goal."""
        goal = await self.get_goal(db, goal_id, user_id)
        if not goal:
            return False
        
        await db.delete(goal)
        await db.commit()
        return True
    
    async def add_contribution(
        self,
        db: AsyncSession,
        goal_id: UUID,
        user_id: UUID,
        contribution_data: ContributionCreate
    ) -> Optional[GoalContribution]:
        """Add a contribution to a goal."""
        goal = await self.get_goal(db, goal_id, user_id)
        if not goal:
            return None
        
        # Create contribution
        contribution = GoalContribution(
            goal_id=goal_id,
            user_id=user_id,
            **contribution_data.model_dump()
        )
        
        # Update goal current amount (convert to Decimal for proper arithmetic with Numeric columns)
        goal.current_amount = Decimal(str(goal.current_amount)) + Decimal(str(contribution.amount))
        
        # Check if goal is completed
        if Decimal(str(goal.current_amount)) >= Decimal(str(goal.target_amount)):
            goal.status = GoalStatus.COMPLETED
            goal.completed_at = datetime.utcnow()
        else:
            # Update projection
            await self._update_goal_projection(db, goal, user_id)
        
        db.add(contribution)
        await db.commit()
        await db.refresh(contribution)
        return contribution
    
    async def get_contributions(
        self,
        db: AsyncSession,
        goal_id: UUID,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[GoalContribution]:
        """Get contributions for a goal."""
        result = await db.execute(
            select(GoalContribution)
            .where(and_(
                GoalContribution.goal_id == goal_id,
                GoalContribution.user_id == user_id
            ))
            .order_by(GoalContribution.contributed_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def pause_goal(
        self,
        db: AsyncSession,
        goal_id: UUID,
        user_id: UUID
    ) -> Optional[Goal]:
        """Pause an active goal."""
        goal = await self.get_goal(db, goal_id, user_id)
        if not goal or goal.status != GoalStatus.ACTIVE:
            return None
        
        goal.status = GoalStatus.PAUSED
        await db.commit()
        await db.refresh(goal)
        return goal
    
    async def resume_goal(
        self,
        db: AsyncSession,
        goal_id: UUID,
        user_id: UUID
    ) -> Optional[Goal]:
        """Resume a paused goal."""
        goal = await self.get_goal(db, goal_id, user_id)
        if not goal or goal.status != GoalStatus.PAUSED:
            return None
        
        goal.status = GoalStatus.ACTIVE
        await self._update_goal_projection(db, goal, user_id)
        await db.commit()
        await db.refresh(goal)
        return goal
    
    async def complete_goal(
        self,
        db: AsyncSession,
        goal_id: UUID,
        user_id: UUID
    ) -> Optional[Goal]:
        """Manually mark a goal as completed."""
        goal = await self.get_goal(db, goal_id, user_id)
        if not goal:
            return None
        
        goal.status = GoalStatus.COMPLETED
        goal.completed_at = datetime.utcnow()
        await db.commit()
        await db.refresh(goal)
        return goal
    
    async def analyze_feasibility(
        self,
        db: AsyncSession,
        goal_id: UUID,
        user_id: UUID
    ) -> Optional[FeasibilityAnalysis]:
        """
        Analyze the feasibility of achieving a goal based on
        current savings rate and spending patterns.
        """
        goal = await self.get_goal(db, goal_id, user_id)
        if not goal:
            return None
        
        # Calculate current savings rate from contributions
        contributions = await self.get_contributions(db, goal_id, user_id, limit=100)
        
        if not contributions:
            # No contribution history yet
            remaining = goal.target_amount - goal.current_amount
            
            if not goal.target_date:
                return FeasibilityAnalysis(
                    is_achievable=True,
                    confidence_level="low",
                    estimated_completion_date=None,
                    required_monthly_savings=0.0,
                    current_savings_rate=0.0,
                    recommendations=[
                        "Start making contributions to track your progress",
                        "Set up automatic contributions if possible",
                        "Enable round-up savings for passive contributions"
                    ]
                )
            
            # Calculate required monthly savings
            days_remaining = (goal.target_date - date.today()).days
            months_remaining = max(1, days_remaining / 30)
            required_monthly = remaining / months_remaining
            
            return FeasibilityAnalysis(
                is_achievable=True,
                confidence_level="low",
                estimated_completion_date=goal.target_date,
                required_monthly_savings=required_monthly,
                current_savings_rate=0.0,
                recommendations=[
                    f"You need to save ${required_monthly:.2f} per month to reach your goal",
                    "Start tracking your contributions to get personalized insights",
                    "Consider setting up automatic transfers"
                ]
            )
        
        # Calculate savings rate from recent contributions (last 90 days)
        recent_date = datetime.utcnow() - timedelta(days=90)
        recent_contributions = [
            c for c in contributions 
            if c.contributed_at >= recent_date
        ]
        
        if recent_contributions:
            total_contributed = sum(c.amount for c in recent_contributions)
            days_tracked = (datetime.utcnow() - min(c.contributed_at for c in recent_contributions)).days
            months_tracked = max(1, days_tracked / 30)
            monthly_rate = total_contributed / months_tracked
        else:
            monthly_rate = 0.0
        
        # Calculate what's needed
        remaining = goal.target_amount - goal.current_amount
        
        if not goal.target_date:
            # No target date, estimate based on current rate
            if monthly_rate > 0:
                months_needed = remaining / monthly_rate
                estimated_date = date.today() + timedelta(days=int(months_needed * 30))
            else:
                estimated_date = None
            
            return FeasibilityAnalysis(
                is_achievable=monthly_rate > 0,
                confidence_level="medium" if monthly_rate > 0 else "low",
                estimated_completion_date=estimated_date,
                required_monthly_savings=0.0,
                current_savings_rate=monthly_rate,
                recommendations=self._generate_recommendations(
                    monthly_rate, 0.0, remaining, None
                )
            )
        
        # Calculate required rate to meet target date
        days_remaining = (goal.target_date - date.today()).days
        if days_remaining <= 0:
            return FeasibilityAnalysis(
                is_achievable=False,
                confidence_level="high",
                estimated_completion_date=None,
                required_monthly_savings=0.0,
                current_savings_rate=monthly_rate,
                shortfall_per_month=None,
                recommendations=[
                    "Your target date has passed",
                    "Consider extending the target date or reducing the goal amount",
                    "Review your progress and adjust expectations"
                ]
            )
        
        months_remaining = max(1, days_remaining / 30)
        required_monthly = remaining / months_remaining
        
        shortfall = required_monthly - monthly_rate if monthly_rate < required_monthly else None
        is_achievable = monthly_rate >= required_monthly * 0.8  # 80% threshold
        
        if monthly_rate >= required_monthly:
            confidence = "high"
        elif monthly_rate >= required_monthly * 0.6:
            confidence = "medium"
        else:
            confidence = "low"
        
        # Calculate scenarios
        scenario_10_percent = None
        scenario_reduce_spending = None
        
        if shortfall and shortfall > 0:
            # 10% increase scenario
            new_rate = monthly_rate * 1.1
            if new_rate >= required_monthly:
                new_months = remaining / new_rate
                scenario_10_percent = {
                    "new_monthly_rate": new_rate,
                    "estimated_completion": date.today() + timedelta(days=int(new_months * 30))
                }
            
            # Spending reduction scenario (save $200/month more)
            spending_savings = 200
            new_rate_spending = monthly_rate + spending_savings
            if new_rate_spending >= required_monthly:
                new_months = remaining / new_rate_spending
                scenario_reduce_spending = {
                    "monthly_savings_increase": spending_savings,
                    "new_monthly_rate": new_rate_spending,
                    "estimated_completion": date.today() + timedelta(days=int(new_months * 30))
                }
        
        return FeasibilityAnalysis(
            is_achievable=is_achievable,
            confidence_level=confidence,
            estimated_completion_date=goal.target_date if is_achievable else None,
            required_monthly_savings=required_monthly,
            current_savings_rate=monthly_rate,
            shortfall_per_month=shortfall,
            recommendations=self._generate_recommendations(
                monthly_rate, required_monthly, remaining, goal.target_date
            ),
            scenario_if_increase_10_percent=scenario_10_percent,
            scenario_if_reduce_spending=scenario_reduce_spending
        )
    
    def _generate_recommendations(
        self,
        current_rate: float,
        required_rate: float,
        remaining: float,
        target_date: Optional[date]
    ) -> List[str]:
        """Generate personalized recommendations."""
        recommendations = []
        
        if current_rate == 0:
            recommendations.append("Start making regular contributions to build momentum")
            recommendations.append("Even small amounts add up over time")
            return recommendations
        
        if required_rate == 0 or not target_date:
            recommendations.append(f"Keep up your current pace of ${current_rate:.2f}/month")
            recommendations.append("Consider setting a target date for more focused progress")
            return recommendations
        
        shortfall = required_rate - current_rate
        
        if shortfall <= 0:
            recommendations.append("You're on track! Keep up the great work")
            recommendations.append("Consider increasing contributions to finish early")
        elif shortfall <= current_rate * 0.2:
            recommendations.append(f"You're close! Increase by ${shortfall:.2f}/month to stay on track")
            recommendations.append("Small adjustments can make a big difference")
        else:
            recommendations.append(f"Increase contributions by ${shortfall:.2f}/month to meet your goal")
            recommendations.append("Consider extending your target date for a more achievable pace")
            recommendations.append("Look for areas to reduce spending and redirect to this goal")
        
        # Add specific tactics
        if remaining > 1000:
            recommendations.append("Enable round-up savings for passive contributions")
        if target_date:
            days_left = (target_date - date.today()).days
            if days_left > 90:
                recommendations.append("Set up automatic transfers to stay consistent")
        
        return recommendations
    
    async def _update_goal_projection(
        self,
        db: AsyncSession,
        goal: Goal,
        user_id: UUID
    ) -> None:
        """Update goal projection based on current progress."""
        if not goal.target_date:
            return
        
        # Get recent contribution rate
        contributions = await self.get_contributions(db, goal.id, user_id, limit=20)
        
        if not contributions or len(contributions) < 2:
            # Not enough data for projection
            days_remaining = (goal.target_date - date.today()).days
            remaining = goal.target_amount - goal.current_amount
            
            if goal.monthly_target and goal.monthly_target > 0:
                months_needed = remaining / goal.monthly_target
                projected_date = date.today() + timedelta(days=int(months_needed * 30))
                goal.projected_completion_date = projected_date
                goal.is_on_track = projected_date <= goal.target_date
            else:
                goal.is_on_track = days_remaining > 0
            return
        
        # Calculate average monthly contribution
        recent_date = datetime.utcnow() - timedelta(days=90)
        recent_contributions = [
            c for c in contributions 
            if c.contributed_at >= recent_date
        ]
        
        if recent_contributions:
            total_contributed = sum(c.amount for c in recent_contributions)
            days_tracked = (datetime.utcnow() - min(c.contributed_at for c in recent_contributions)).days
            months_tracked = max(1, days_tracked / 30)
            monthly_rate = total_contributed / months_tracked
            
            # Project completion date
            remaining = goal.target_amount - goal.current_amount
            if monthly_rate > 0:
                months_needed = remaining / monthly_rate
                projected_date = date.today() + timedelta(days=int(months_needed * 30))
                goal.projected_completion_date = projected_date
                goal.is_on_track = projected_date <= goal.target_date
            else:
                goal.is_on_track = False
        else:
            goal.is_on_track = False
    
    async def calculate_roundup_savings(
        self,
        db: AsyncSession,
        user_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> float:
        """
        Calculate potential round-up savings from transactions.
        Rounds each transaction up to the nearest dollar.
        """
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()
        
        # Get transactions in date range
        result = await db.execute(
            select(Transaction)
            .where(and_(
                Transaction.user_id == user_id,
                Transaction.date >= start_date,
                Transaction.date <= end_date,
                Transaction.amount < 0  # Only expenses (negative amounts)
            ))
        )
        transactions = result.scalars().all()
        
        # Calculate round-up amounts
        total_roundup = 0.0
        for transaction in transactions:
            amount = abs(transaction.amount)
            rounded_up = (int(amount) + 1) if amount != int(amount) else amount
            roundup = rounded_up - amount
            total_roundup += roundup
        
        return round(total_roundup, 2)


# Singleton instance
goal_service = GoalService()
