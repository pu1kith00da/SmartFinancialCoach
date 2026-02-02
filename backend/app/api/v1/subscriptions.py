from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.subscription import SubscriptionStatus
from app.services.subscription_service import SubscriptionService
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionUpdate,
    SubscriptionResponse,
    SubscriptionDetectionResponse,
    SubscriptionStats,
    SubscriptionBulkAction
)

router = APIRouter()


@router.post("/", response_model=SubscriptionResponse, status_code=201)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new subscription."""
    # Placeholder - return mock data for now
    from uuid import uuid4
    return {
        "id": uuid4(),
        "user_id": current_user.id,
        "name": subscription_data.name,
        "service_provider": subscription_data.service_provider,
        "category": subscription_data.category,
        "amount": subscription_data.amount,
        "billing_cycle": subscription_data.billing_cycle,
        "first_charge_date": subscription_data.first_charge_date,
        "next_billing_date": subscription_data.first_charge_date,
        "status": "active",
        "detection_confidence": "manual",
        "auto_detected": False,
        "confirmed_by_user": True,
        "monthly_cost": subscription_data.amount,
        "annual_cost": subscription_data.amount * 12,
        "days_until_next_billing": 30,
        "is_trial_expiring_soon": False,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }


@router.get("/", response_model=List[SubscriptionResponse])
async def get_subscriptions(
    status: Optional[SubscriptionStatus] = Query(None, description="Filter by subscription status"),
    limit: Optional[int] = Query(50, le=100, description="Number of subscriptions to return"),
    offset: int = Query(0, ge=0, description="Number of subscriptions to skip"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's subscriptions with optional filtering."""
    service = SubscriptionService(db)
    subscriptions = await service.get_user_subscriptions(
        current_user.id,
        status=status,
        limit=limit,
        offset=offset
    )
    return subscriptions


@router.get("/stats", response_model=SubscriptionStats)
async def get_subscription_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get subscription statistics for the user."""
    service = SubscriptionService(db)
    stats = await service.get_subscription_stats(current_user.id)
    return stats


@router.get("/detect", response_model=List[SubscriptionDetectionResponse])
async def detect_subscriptions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Detect potential subscriptions from transaction patterns."""
    service = SubscriptionService(db)
    detections = service.detect_recurring_charges(current_user.id)
    return detections


@router.get("/calendar")
async def get_subscription_calendar(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get subscription calendar for a date range."""
    # Placeholder implementation
    return {"message": "Calendar functionality coming soon"}


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific subscription by ID."""
    service = SubscriptionService(db)
    try:
        subscription = service.get_subscription(current_user.id, subscription_id)
        return subscription
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Subscription not found")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: UUID,
    subscription_data: SubscriptionUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an existing subscription."""
    service = SubscriptionService(db)
    try:
        subscription = service.update_subscription(
            current_user.id, subscription_id, subscription_data
        )
        return subscription
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Subscription not found")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{subscription_id}", status_code=204)
async def cancel_subscription(
    subscription_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Cancel a subscription."""
    service = SubscriptionService(db)
    try:
        service.cancel_subscription(current_user.id, subscription_id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Subscription not found")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-action", status_code=204)
async def bulk_subscription_action(
    action_data: SubscriptionBulkAction,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Perform bulk actions on multiple subscriptions."""
    service = SubscriptionService(db)
    
    if action_data.action not in ["cancel", "pause", "resume"]:
        raise HTTPException(status_code=400, detail="Invalid action. Use: cancel, pause, resume")
    
    # Process each subscription
    for subscription_id in action_data.subscription_ids:
        try:
            if action_data.action == "cancel":
                service.cancel_subscription(current_user.id, subscription_id)
            elif action_data.action == "pause":
                # Implement pause logic (update status to PAUSED)
                service.update_subscription(
                    current_user.id, 
                    subscription_id, 
                    SubscriptionUpdate(status=SubscriptionStatus.PAUSED)
                )
            elif action_data.action == "resume":
                # Implement resume logic (update status to ACTIVE)
                service.update_subscription(
                    current_user.id, 
                    subscription_id, 
                    SubscriptionUpdate(status=SubscriptionStatus.ACTIVE)
                )
        except Exception as e:
            # Log error but continue with other subscriptions
            print(f"Error processing subscription {subscription_id}: {e}")
            continue


@router.post("/detect/{detection_id}/confirm", response_model=SubscriptionResponse)
async def confirm_detected_subscription(
    detection_id: str,
    confirm: bool = Query(True, description="Whether to confirm or reject the detection"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Confirm or reject a detected subscription pattern."""
    service = SubscriptionService(db)
    
    if not confirm:
        # Just return success for rejection
        return {"message": "Detection rejected"}
    
    try:
        subscription = service.confirm_detected_subscription(
            current_user.id, detection_id, confirm
        )
        if subscription:
            return subscription
        else:
            raise HTTPException(status_code=404, detail="Detection not found or already processed")
    except NotImplementedError:
        raise HTTPException(status_code=501, detail="Detection confirmation not yet implemented")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{subscription_id}/pause", response_model=SubscriptionResponse)
async def pause_subscription(
    subscription_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Pause a subscription."""
    service = SubscriptionService(db)
    try:
        subscription = service.update_subscription(
            current_user.id,
            subscription_id,
            SubscriptionUpdate(status=SubscriptionStatus.PAUSED)
        )
        return subscription
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Subscription not found")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{subscription_id}/resume", response_model=SubscriptionResponse)
async def resume_subscription(
    subscription_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Resume a paused subscription."""
    service = SubscriptionService(db)
    try:
        subscription = service.update_subscription(
            current_user.id,
            subscription_id,
            SubscriptionUpdate(status=SubscriptionStatus.ACTIVE)
        )
        return subscription
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Subscription not found")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{subscription_id}/usage-history")
async def get_subscription_usage_history(
    subscription_id: UUID,
    months: int = Query(6, ge=1, le=24, description="Number of months to retrieve"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get usage history for a subscription."""
    # This would integrate with usage tracking if implemented
    # For now, return a placeholder
    return {
        "subscription_id": subscription_id,
        "usage_history": [],
        "message": "Usage tracking not yet implemented"
    }


@router.put("/{subscription_id}/usage")
async def update_subscription_usage(
    subscription_id: UUID,
    usage_data: dict,  # Would use a proper schema in production
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update usage information for a subscription."""
    # This would update usage tracking if implemented
    return {
        "subscription_id": subscription_id,
        "message": "Usage updated successfully"
    }