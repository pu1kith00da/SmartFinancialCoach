"""
GDPR Compliance endpoints - Data deletion and export
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import json

from app.core.database import get_db
from app.models.user import User
from app.models.transaction import Transaction
from app.models.plaid import Account
# from app.models.analytics import Budget  # Not implemented yet
from app.models.goal import Goal
from app.models.subscription import Subscription
from app.models.bill import Bill
from app.models.insight import Insight
from app.models.gamification import UserAchievement, UserChallenge, Streak, XPHistory
from app.api.dependencies import get_current_user
from app.core.logging import get_logger, log_with_context

router = APIRouter()
logger = get_logger(__name__)


class DataExportRequest(BaseModel):
    """Request for data export"""
    include_transactions: bool = True
    include_accounts: bool = True
    include_budgets: bool = True
    include_goals: bool = True
    include_subscriptions: bool = True
    include_bills: bool = True
    include_insights: bool = True
    include_gamification: bool = True


class DataExportResponse(BaseModel):
    """Response for data export"""
    user_id: str
    export_date: str
    data: dict


class DataDeletionRequest(BaseModel):
    """Request for account deletion"""
    confirmation: str  # User must type "DELETE MY ACCOUNT"
    reason: Optional[str] = None


class DataDeletionResponse(BaseModel):
    """Response for account deletion"""
    message: str
    user_id: str
    deletion_date: str
    items_deleted: dict


@router.post("/gdpr/export", response_model=DataExportResponse)
async def export_user_data(
    request: DataExportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Export all user data in machine-readable format (GDPR Article 20).
    Returns a complete JSON export of the user's data.
    """
    log_with_context(
        logger,
        "info",
        "User data export requested",
        user_id=str(current_user.id)
    )
    
    export_data = {
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "level": current_user.level,
            "xp": current_user.xp,
        }
    }
    
    # Export transactions
    if request.include_transactions:
        transactions_result = await db.execute(
            select(Transaction).where(Transaction.user_id == current_user.id)
        )
        transactions = transactions_result.scalars().all()
        export_data["transactions"] = [
            {
                "id": str(t.id),
                "account_id": str(t.account_id),
                "amount": float(t.amount),
                "category": t.category,
                "subcategory": t.subcategory,
                "description": t.description,
                "merchant_name": t.merchant_name,
                "date": t.date.isoformat() if t.date else None,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in transactions
        ]
    
    # Export accounts
    if request.include_accounts:
        accounts_result = await db.execute(
            select(Account).where(Account.user_id == current_user.id)
        )
        accounts = accounts_result.scalars().all()
        export_data["accounts"] = [
            {
                "id": str(a.id),
                "plaid_account_id": a.plaid_account_id,
                "name": a.name,
                "type": a.type,
                "subtype": a.subtype,
                "balance_available": float(a.balance_available) if a.balance_available else None,
                "balance_current": float(a.balance_current) if a.balance_current else None,
                "currency_code": a.currency_code,
                "created_at": a.created_at.isoformat() if a.created_at else None,
            }
            for a in accounts
        ]
    
    # Export budgets
    if request.include_budgets:
        # Budget model not yet implemented
        export_data["budgets"] = []
        # budgets_result = await db.execute(
        #     select(Budget).where(Budget.user_id == current_user.id)
        # )
        # budgets = budgets_result.scalars().all()
        # export_data["budgets"] = [
        #     {
        #         "id": str(b.id),
        #         "category": b.category,
        #         "amount": float(b.amount),
        #         "period": b.period,
        #         "start_date": b.start_date.isoformat() if b.start_date else None,
        #         "end_date": b.end_date.isoformat() if b.end_date else None,
        #         "created_at": b.created_at.isoformat() if b.created_at else None,
        #     }
        #     for b in budgets
        # ]
    
    # Export goals
    if request.include_goals:
        goals_result = await db.execute(
            select(Goal).where(Goal.user_id == current_user.id)
        )
        goals = goals_result.scalars().all()
        export_data["goals"] = [
            {
                "id": str(g.id),
                "name": g.name,
                "description": g.description,
                "target_amount": float(g.target_amount),
                "current_amount": float(g.current_amount),
                "target_date": g.target_date.isoformat() if g.target_date else None,
                "status": g.status,
                "created_at": g.created_at.isoformat() if g.created_at else None,
            }
            for g in goals
        ]
    
    # Export subscriptions
    if request.include_subscriptions:
        subscriptions_result = await db.execute(
            select(Subscription).where(Subscription.user_id == current_user.id)
        )
        subscriptions = subscriptions_result.scalars().all()
        export_data["subscriptions"] = [
            {
                "id": str(s.id),
                "name": s.name,
                "amount": float(s.amount),
                "billing_cycle": s.billing_cycle,
                "next_billing_date": s.next_billing_date.isoformat() if s.next_billing_date else None,
                "category": s.category,
                "status": s.status,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in subscriptions
        ]
    
    # Export bills
    if request.include_bills:
        bills_result = await db.execute(
            select(Bill).where(Bill.user_id == current_user.id)
        )
        bills = bills_result.scalars().all()
        export_data["bills"] = [
            {
                "id": str(b.id),
                "name": b.name,
                "amount": float(b.amount) if b.amount else None,
                "due_date": b.due_date.isoformat() if b.due_date else None,
                "category": b.category,
                "status": b.status,
                "created_at": b.created_at.isoformat() if b.created_at else None,
            }
            for b in bills
        ]
    
    # Export insights
    if request.include_insights:
        insights_result = await db.execute(
            select(Insight).where(Insight.user_id == current_user.id)
        )
        insights = insights_result.scalars().all()
        export_data["insights"] = [
            {
                "id": str(i.id),
                "type": i.type,
                "title": i.title,
                "message": i.message,
                "priority": i.priority,
                "created_at": i.created_at.isoformat() if i.created_at else None,
            }
            for i in insights
        ]
    
    # Export gamification data
    if request.include_gamification:
        # User achievements
        achievements_result = await db.execute(
            select(UserAchievement).where(UserAchievement.user_id == current_user.id)
        )
        achievements = achievements_result.scalars().all()
        
        # User challenges
        challenges_result = await db.execute(
            select(UserChallenge).where(UserChallenge.user_id == current_user.id)
        )
        challenges = challenges_result.scalars().all()
        
        # Streak
        streak_result = await db.execute(
            select(Streak).where(Streak.user_id == current_user.id)
        )
        streak = streak_result.scalar_one_or_none()
        
        # XP history
        xp_result = await db.execute(
            select(XPHistory).where(XPHistory.user_id == current_user.id)
        )
        xp_history = xp_result.scalars().all()
        
        export_data["gamification"] = {
            "achievements": [
                {
                    "achievement_id": str(a.achievement_id),
                    "unlocked_at": a.unlocked_at.isoformat() if a.unlocked_at else None,
                }
                for a in achievements
            ],
            "challenges": [
                {
                    "challenge_id": str(c.challenge_id),
                    "status": c.status,
                    "progress": c.progress,
                    "started_at": c.started_at.isoformat() if c.started_at else None,
                    "completed_at": c.completed_at.isoformat() if c.completed_at else None,
                }
                for c in challenges
            ],
            "streak": {
                "current_streak": streak.current_streak if streak else 0,
                "longest_streak": streak.longest_streak if streak else 0,
                "total_activity_days": streak.total_activity_days if streak else 0,
            } if streak else None,
            "xp_history": [
                {
                    "xp_amount": xp.xp_amount,
                    "source": xp.source,
                    "description": xp.description,
                    "created_at": xp.created_at.isoformat() if xp.created_at else None,
                }
                for xp in xp_history
            ]
        }
    
    log_with_context(
        logger,
        "info",
        "User data export completed",
        user_id=str(current_user.id),
        export_size_kb=len(json.dumps(export_data)) / 1024
    )
    
    return DataExportResponse(
        user_id=str(current_user.id),
        export_date=datetime.utcnow().isoformat() + "Z",
        data=export_data
    )


async def delete_user_data_background(user_id: str, db: AsyncSession):
    """Background task to delete user data"""
    try:
        # Delete in order respecting foreign key constraints
        
        # Delete gamification data
        await db.execute(delete(XPHistory).where(XPHistory.user_id == user_id))
        await db.execute(delete(UserChallenge).where(UserChallenge.user_id == user_id))
        await db.execute(delete(UserAchievement).where(UserAchievement.user_id == user_id))
        await db.execute(delete(Streak).where(Streak.user_id == user_id))
        
        # Delete insights
        await db.execute(delete(Insight).where(Insight.user_id == user_id))
        
        # Delete bills
        await db.execute(delete(Bill).where(Bill.user_id == user_id))
        
        # Delete subscriptions
        await db.execute(delete(Subscription).where(Subscription.user_id == user_id))
        
        # Delete goals
        await db.execute(delete(Goal).where(Goal.user_id == user_id))
        
        # Delete budgets (not yet implemented)
        # await db.execute(delete(Budget).where(Budget.user_id == user_id))
        
        # Delete transactions
        await db.execute(delete(Transaction).where(Transaction.user_id == user_id))
        
        # Delete accounts
        await db.execute(delete(Account).where(Account.user_id == user_id))
        
        # Finally, delete user
        await db.execute(delete(User).where(User.id == user_id))
        
        await db.commit()
        
        log_with_context(
            logger,
            "info",
            "User account completely deleted",
            user_id=user_id
        )
    except Exception as e:
        await db.rollback()
        log_with_context(
            logger,
            "error",
            "Failed to delete user account",
            user_id=user_id,
            error=str(e)
        )
        raise


@router.post("/gdpr/delete", response_model=DataDeletionResponse)
async def delete_user_account(
    request: DataDeletionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Permanently delete user account and all associated data (GDPR Article 17).
    This action is irreversible.
    """
    # Verify confirmation
    if request.confirmation != "DELETE MY ACCOUNT":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Confirmation must be exactly "DELETE MY ACCOUNT"'
        )
    
    log_with_context(
        logger,
        "warning",
        "User account deletion requested",
        user_id=str(current_user.id),
        reason=request.reason
    )
    
    # Count items to be deleted
    transactions_count = await db.scalar(
        select(func.count(Transaction.id)).where(Transaction.user_id == current_user.id)
    )
    accounts_count = await db.scalar(
        select(func.count(Account.id)).where(Account.user_id == current_user.id)
    )
    # budgets_count = await db.scalar(
    #     select(func.count(Budget.id)).where(Budget.user_id == current_user.id)
    # )
    budgets_count = 0  # Budget model not yet implemented
    goals_count = await db.scalar(
        select(func.count(Goal.id)).where(Goal.user_id == current_user.id)
    )
    
    # Schedule deletion in background
    # Note: In production, you might want to add a grace period before actual deletion
    background_tasks.add_task(delete_user_data_background, str(current_user.id), db)
    
    return DataDeletionResponse(
        message="Account deletion has been initiated. All your data will be permanently deleted.",
        user_id=str(current_user.id),
        deletion_date=datetime.utcnow().isoformat() + "Z",
        items_deleted={
            "transactions": transactions_count or 0,
            "accounts": accounts_count or 0,
            "budgets": budgets_count or 0,
            "goals": goals_count or 0,
        }
    )


from sqlalchemy import func
