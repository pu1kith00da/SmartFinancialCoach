from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.bill import BillStatus, BillCategory, BillFrequency
from app.services.bill_service import BillService
from app.schemas.bill import (
    BillCreate,
    BillUpdate,
    BillResponse,
    BillPaymentCreate,
    BillPaymentUpdate,
    BillPaymentResponse,
    BillStats,
    BillDetectionResult,
    BillBulkAction,
    BillReminderSettings
)

router = APIRouter()


@router.post("/", response_model=BillResponse, status_code=201)
async def create_bill(
    bill_data: BillCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new bill."""
    service = BillService(db)
    bill = service.create_bill(current_user.id, bill_data)
    return bill


@router.get("/", response_model=List[BillResponse])
async def get_bills(
    status: Optional[BillStatus] = Query(None, description="Filter by bill status"),
    category: Optional[BillCategory] = Query(None, description="Filter by category"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    due_soon: Optional[bool] = Query(False, description="Filter bills due within 7 days"),
    limit: Optional[int] = Query(50, le=100, description="Number of bills to return"),
    offset: int = Query(0, ge=0, description="Number of bills to skip"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's bills with optional filtering."""
    service = BillService(db)
    bills = service.get_user_bills(
        user_id=current_user.id,
        status=status,
        category=category,
        is_active=is_active,
        due_soon=due_soon,
        limit=limit,
        offset=offset
    )
    return bills


@router.get("/stats", response_model=BillStats)
async def get_bill_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get bill statistics for the user."""
    service = BillService(db)
    stats = service.get_bill_stats(current_user.id)
    return stats


@router.get("/detect", response_model=List[BillDetectionResult])
async def detect_bills(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Detect potential bills from transaction patterns."""
    service = BillService(db)
    detections = service.detect_bills_from_transactions(current_user.id)
    return detections


@router.get("/upcoming", response_model=List[BillResponse])
async def get_upcoming_bills(
    days_ahead: int = Query(7, ge=1, le=30, description="Number of days to look ahead"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get bills due in the next N days."""
    service = BillService(db)
    bills = service.get_upcoming_bills(current_user.id, days_ahead)
    return bills


@router.get("/calendar")
async def get_bill_calendar(
    start_date: str = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: str = Query(..., description="End date in YYYY-MM-DD format"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get bill calendar for a date range."""
    # Placeholder implementation
    return {"message": "Calendar functionality coming soon"}


@router.get("/{bill_id}", response_model=BillResponse)
async def get_bill(
    bill_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific bill by ID."""
    service = BillService(db)
    try:
        bill = service.get_bill(current_user.id, bill_id)
        return bill
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Bill not found")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{bill_id}", response_model=BillResponse)
async def update_bill(
    bill_id: UUID,
    bill_data: BillUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update an existing bill."""
    service = BillService(db)
    try:
        bill = service.update_bill(current_user.id, bill_id, bill_data)
        return bill
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Bill not found")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{bill_id}", status_code=204)
async def delete_bill(
    bill_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a bill."""
    service = BillService(db)
    try:
        service.delete_bill(current_user.id, bill_id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Bill not found")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{bill_id}/deactivate", response_model=BillResponse)
async def deactivate_bill(
    bill_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Deactivate a bill instead of deleting."""
    service = BillService(db)
    try:
        bill = service.deactivate_bill(current_user.id, bill_id)
        return bill
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Bill not found")
        raise HTTPException(status_code=500, detail=str(e))


# Bill Payment endpoints

@router.post("/{bill_id}/payments", response_model=BillPaymentResponse, status_code=201)
async def create_payment(
    bill_id: UUID,
    payment_data: BillPaymentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Record a bill payment."""
    service = BillService(db)
    try:
        payment = service.create_payment(current_user.id, bill_id, payment_data)
        return payment
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Bill not found")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payments", response_model=List[BillPaymentResponse])
async def get_payments(
    bill_id: Optional[UUID] = Query(None, description="Filter by bill ID"),
    start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format"),
    end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format"),
    limit: Optional[int] = Query(50, le=100, description="Number of payments to return"),
    offset: int = Query(0, ge=0, description="Number of payments to skip"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get bill payments with optional filtering."""
    # Parse dates if provided
    parsed_start_date = None
    parsed_end_date = None
    
    if start_date:
        try:
            from datetime import datetime
            parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
    
    if end_date:
        try:
            from datetime import datetime
            parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")
    
    service = BillService(db)
    payments = service.get_bill_payments(
        user_id=current_user.id,
        bill_id=bill_id,
        start_date=parsed_start_date,
        end_date=parsed_end_date,
        limit=limit,
        offset=offset
    )
    return payments


@router.get("/{bill_id}/payments", response_model=List[BillPaymentResponse])
async def get_bill_payments(
    bill_id: UUID,
    limit: Optional[int] = Query(50, le=100, description="Number of payments to return"),
    offset: int = Query(0, ge=0, description="Number of payments to skip"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get payments for a specific bill."""
    service = BillService(db)
    payments = service.get_bill_payments(
        user_id=current_user.id,
        bill_id=bill_id,
        limit=limit,
        offset=offset
    )
    return payments


@router.get("/payments/{payment_id}", response_model=BillPaymentResponse)
async def get_payment(
    payment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific payment by ID."""
    service = BillService(db)
    try:
        payment = service.get_payment(current_user.id, payment_id)
        return payment
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Payment not found")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/payments/{payment_id}", response_model=BillPaymentResponse)
async def update_payment(
    payment_id: UUID,
    payment_data: BillPaymentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a bill payment."""
    service = BillService(db)
    try:
        payment = service.update_payment(current_user.id, payment_id, payment_data)
        return payment
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Payment not found")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/payments/{payment_id}", status_code=204)
async def delete_payment(
    payment_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a bill payment."""
    service = BillService(db)
    try:
        service.delete_payment(current_user.id, payment_id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Payment not found")
        raise HTTPException(status_code=500, detail=str(e))


# Bulk operations and utilities

@router.post("/bulk-action", status_code=204)
async def bulk_bill_action(
    action_data: BillBulkAction,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Perform bulk actions on multiple bills."""
    service = BillService(db)
    
    if action_data.action not in ["activate", "deactivate", "delete"]:
        raise HTTPException(status_code=400, detail="Invalid action. Use: activate, deactivate, delete")
    
    # Process each bill
    for bill_id in action_data.bill_ids:
        try:
            if action_data.action == "activate":
                service.update_bill(
                    current_user.id, 
                    bill_id, 
                    BillUpdate(is_active=True, status=BillStatus.PENDING)
                )
            elif action_data.action == "deactivate":
                service.deactivate_bill(current_user.id, bill_id)
            elif action_data.action == "delete":
                service.delete_bill(current_user.id, bill_id)
        except Exception as e:
            # Log error but continue with other bills
            print(f"Error processing bill {bill_id}: {e}")
            continue


@router.post("/update-overdue", status_code=204)
async def update_overdue_bills(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update status for overdue bills."""
    service = BillService(db)
    service.update_overdue_bills()


@router.get("/{bill_id}/reminder-settings", response_model=BillReminderSettings)
async def get_reminder_settings(
    bill_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get reminder settings for a bill."""
    service = BillService(db)
    try:
        bill = service.get_bill(current_user.id, bill_id)
        
        # Create reminder settings from bill data
        return BillReminderSettings(
            bill_id=bill.id,
            email_enabled=True,  # Default values - would be stored in bill model
            push_enabled=True,
            days_before=[bill.reminder_days_before],
            custom_message=None
        )
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Bill not found")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{bill_id}/reminder-settings", response_model=BillReminderSettings)
async def update_reminder_settings(
    bill_id: UUID,
    reminder_settings: BillReminderSettings,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update reminder settings for a bill."""
    service = BillService(db)
    try:
        # Update the bill's reminder days (would expand to include other settings)
        service.update_bill(
            current_user.id,
            bill_id,
            BillUpdate(reminder_days_before=reminder_settings.days_before[0] if reminder_settings.days_before else 3)
        )
        
        return reminder_settings
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail="Bill not found")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/categories/summary")
async def get_categories_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get summary of bills by category."""
    service = BillService(db)
    bills = service.get_user_bills(current_user.id, is_active=True)
    
    category_summary = {}
    for bill in bills:
        category = bill.category
        if category not in category_summary:
            category_summary[category] = {
                "count": 0,
                "total_monthly": 0,
                "bills": []
            }
        
        category_summary[category]["count"] += 1
        category_summary[category]["total_monthly"] += bill.monthly_amount
        category_summary[category]["bills"].append({
            "id": str(bill.id),
            "name": bill.name,
            "amount": bill.monthly_amount
        })
    
    return category_summary


@router.get("/frequency/analysis")
async def get_frequency_analysis(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get analysis of bill frequencies."""
    service = BillService(db)
    bills = service.get_user_bills(current_user.id, is_active=True)
    
    frequency_analysis = {}
    for frequency in BillFrequency:
        frequency_bills = [b for b in bills if b.frequency == frequency.value]
        frequency_analysis[frequency.value] = {
            "count": len(frequency_bills),
            "total_monthly_equivalent": sum(b.monthly_amount for b in frequency_bills),
            "average_amount": sum(b.monthly_amount for b in frequency_bills) / len(frequency_bills) if frequency_bills else 0
        }
    
    return frequency_analysis