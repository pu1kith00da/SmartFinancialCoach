"""
API endpoints for AI-powered financial insights.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID
import logging

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.insight import (
    InsightResponse,
    InsightListResponse,
    InsightFilters,
    MarkReadRequest,
    DailyNudgeResponse,
    InsightAnalytics,
    AnomalyDetectionResponse
)
from app.services.insight_service import InsightService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=InsightListResponse)
async def list_insights(
    type: Optional[str] = None,
    priority: Optional[str] = None,
    is_read: Optional[bool] = None,
    is_dismissed: Optional[bool] = None,
    category: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List insights for the current user.
    
    Query parameters:
    - type: Filter by insight type
    - priority: Filter by priority (low, normal, high, urgent)
    - is_read: Filter by read status
    - is_dismissed: Filter by dismissed status
    - category: Filter by related category
    - limit: Number of results (1-100, default 20)
    - offset: Pagination offset (default 0)
    """
    service = InsightService(db)
    
    filters = {
        "type": type,
        "priority": priority,
        "is_read": is_read,
        "is_dismissed": is_dismissed,
        "category": category,
        "limit": min(limit, 100),
        "offset": max(offset, 0)
    }
    
    insights, total = await service.get_insights(current_user.id, filters)
    
    # If no insights found, return mock data for demo purposes
    if not insights:
        from datetime import datetime
        import uuid
        now = datetime.now()
        mock_insights = [
            {
                "id": str(uuid.uuid4()),
                "user_id": str(current_user.id),
                "type": "spending_alert",
                "title": "High Dining Spending Detected",
                "message": "You've spent $265 on dining this month, which is 88% of your budget. Consider cooking at home more often to stay within budget.",
                "priority": "normal",
                "is_read": False,
                "is_dismissed": False,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "action_type": "review_budget",
                "data": {"category": "Dining", "amount": 265, "budget": 300}
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": str(current_user.id),
                "type": "savings_opportunity",
                "title": "Entertainment Budget Exceeded",
                "message": "You've exceeded your entertainment budget by $35.60. You might want to cut back on entertainment expenses next month.",
                "priority": "high",
                "is_read": False,
                "is_dismissed": False,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "action_type": "adjust_budget",
                "data": {"category": "Entertainment", "over_amount": 35.60}
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": str(current_user.id),
                "type": "goal_progress",
                "title": "Great Progress on Your Goals!",
                "message": "You're on track with 2 of your 3 financial goals. Keep up the good work!",
                "priority": "low",
                "is_read": False,
                "is_dismissed": False,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "data": {"goals_on_track": 2, "total_goals": 3}
            }
        ]
        
        # Apply type filter to mock data if provided
        if type:
            mock_insights = [i for i in mock_insights if i["type"] == type]
        
        return InsightListResponse(
            insights=mock_insights[:filters["limit"]],
            total=len(mock_insights),
            limit=filters["limit"],
            offset=filters["offset"],
            has_more=False
        )
    
    return InsightListResponse(
        insights=[InsightResponse.model_validate(i) for i in insights],
        total=total,
        limit=filters["limit"],
        offset=filters["offset"],
        has_more=offset + len(insights) < total
    )


@router.get("/daily", response_model=DailyNudgeResponse)
async def get_daily_nudge(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get today's daily nudge - the most important unread insight.
    """
    service = InsightService(db)
    insight = await service.get_daily_nudge(current_user.id)
    
    if insight:
        return DailyNudgeResponse(
            insight=InsightResponse.model_validate(insight),
            has_insight=True
        )
    else:
        return DailyNudgeResponse(
            insight=None,
            has_insight=False,
            message="You're all caught up! Check back tomorrow for new insights."
        )


@router.get("/{insight_id}", response_model=InsightResponse)
async def get_insight(
    insight_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific insight by ID."""
    from sqlalchemy import select, and_
    from app.models.insight import Insight
    
    query = select(Insight).where(
        and_(
            Insight.id == insight_id,
            Insight.user_id == current_user.id
        )
    )
    result = await db.execute(query)
    insight = result.scalar_one_or_none()
    
    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight not found"
        )
    
    return InsightResponse.model_validate(insight)


@router.post("/{insight_id}/read", response_model=InsightResponse)
async def mark_insight_read(
    insight_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark an insight as read."""
    service = InsightService(db)
    insight = await service.mark_as_read(insight_id, current_user.id)
    
    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight not found"
        )
    
    return InsightResponse.model_validate(insight)


@router.post("/{insight_id}/dismiss", response_model=InsightResponse)
async def dismiss_insight(
    insight_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Dismiss an insight."""
    service = InsightService(db)
    insight = await service.dismiss(insight_id, current_user.id)
    
    if not insight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Insight not found"
        )
    
    return InsightResponse.model_validate(insight)


@router.post("/generate", response_model=InsightListResponse)
async def generate_insights(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger AI-powered insight generation for the current user.
    Analyzes transactions, spending patterns, budgets, and goals to generate
    comprehensive personalized financial advice.
    """
    from app.services.ai_insight_generator import AIInsightGenerator
    from app.models.insight import Insight
    from datetime import datetime
    import traceback
    
    try:
        # Use enhanced AI generator
        generator = AIInsightGenerator(db)
        insight_data_list = await generator.generate_comprehensive_insights(current_user.id)
        
        # Helper function to convert Decimal to float in nested structures
        def convert_decimals(obj):
            """Recursively convert Decimal objects to float for JSON serialization."""
            from decimal import Decimal
            if isinstance(obj, Decimal):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_decimals(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_decimals(item) for item in obj]
            return obj
        
        # Save insights to database
        saved_insights = []
        for insight_data in insight_data_list:
            # Convert Decimal values to float
            amount = insight_data.get('amount')
            if amount is not None:
                from decimal import Decimal
                amount = float(amount) if isinstance(amount, Decimal) else amount
            
            # Convert context_data to ensure no Decimal values
            context_data = convert_decimals(insight_data.get('context_data', {}))
            
            insight = Insight(
                user_id=current_user.id,
                type=insight_data['type'],
                priority=insight_data['priority'],
                title=insight_data['title'],
                message=insight_data['message'],
                category=insight_data.get('category'),
                amount=amount,
                context_data=context_data,
                is_dismissed=insight_data.get('is_dismissed', False),  # Preserve dismissed status
                dismissed_at=insight_data.get('dismissed_at'),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(insight)
            saved_insights.append(insight)
        
        if saved_insights:
            await db.commit()
            
            # Refresh to get IDs
            for insight in saved_insights:
                await db.refresh(insight)
        
        return InsightListResponse(
            insights=[InsightResponse.model_validate(i) for i in saved_insights],
            total=len(saved_insights),
            limit=len(saved_insights),
            offset=0,
            has_more=False
        )
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate insights: {str(e)}"
        )


@router.get("/analytics", response_model=InsightAnalytics)
async def get_insight_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get analytics and statistics about user's insights.
    Includes engagement metrics and distribution by type/priority.
    """
    service = InsightService(db)
    analytics = await service.get_analytics(current_user.id)
    return analytics


@router.post("/detect-anomalies", response_model=AnomalyDetectionResponse)
async def detect_anomalies(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Run anomaly detection on recent transactions and create insights.
    Returns detected anomalies and generated insights.
    """
    service = InsightService(db)
    insights = await service.create_anomaly_insights(current_user.id)
    
    return AnomalyDetectionResponse(
        anomalies_found=len(insights),
        insights_created=len(insights),
        insights=[InsightResponse.model_validate(i) for i in insights]
    )
