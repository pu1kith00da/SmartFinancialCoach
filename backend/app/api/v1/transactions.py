from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import date, timedelta
from uuid import UUID

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.services.transaction_service import TransactionService
from app.schemas.transaction import (
    TransactionFilterRequest,
    TransactionResponse,
    TransactionListResponse,
    TransactionCreateRequest,
    TransactionUpdateRequest,
    BulkCategorizeRequest,
    TransactionStatsResponse,
    TransactionTypeEnum,
    TransactionStatusEnum
)
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=TransactionListResponse)
async def get_transactions(
    account_ids: Optional[str] = Query(None, description="Comma-separated account UUIDs"),
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    search: Optional[str] = None,
    type: Optional[TransactionTypeEnum] = None,
    status: Optional[TransactionStatusEnum] = None,
    is_recurring: Optional[bool] = None,
    is_excluded: Optional[bool] = False,
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get transactions with filtering and pagination.
    
    Supports filtering by:
    - Account IDs
    - Category
    - Date range
    - Amount range
    - Search term (name or merchant)
    - Type (debit/credit)
    - Status (pending/posted)
    - Recurring status
    """
    try:
        # Parse account IDs
        account_id_list = None
        if account_ids:
            try:
                account_id_list = [UUID(id.strip()) for id in account_ids.split(',')]
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid account_ids format"
                )
        
        # Create filter request
        filters = TransactionFilterRequest(
            account_ids=account_id_list,
            category=category,
            start_date=start_date,
            end_date=end_date,
            min_amount=min_amount,
            max_amount=max_amount,
            search=search,
            type=type,
            status=status,
            is_recurring=is_recurring,
            is_excluded=is_excluded,
            limit=limit,
            offset=offset
        )
        
        transaction_service = TransactionService(db)
        transactions, total = await transaction_service.get_transactions(
            user_id=current_user.id,
            filters=filters
        )
        
        # Convert to response models
        transaction_responses = [
            TransactionResponse.model_validate(t) for t in transactions
        ]
        
        return TransactionListResponse(
            transactions=transaction_responses,
            total=total,
            limit=limit,
            offset=offset,
            has_more=(offset + len(transactions)) < total
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch transactions: {str(e)}"
        )


@router.post("/manual", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_manual_transaction(
    request: TransactionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a manual transaction for cash payments or planned expenses only."""
    transaction_service = TransactionService(db)
    transaction = await transaction_service.create_manual_transaction(
        user_id=current_user.id,
        name=request.name,
        amount=request.amount,
        category=request.category,
        transaction_date=request.transaction_date,
        transaction_type=request.transaction_type,
        notes=request.notes
    )
    
    await db.commit()
    return TransactionResponse.model_validate(transaction)


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific transaction by ID."""
    transaction_service = TransactionService(db)
    transaction = await transaction_service.get_transaction(
        transaction_id=transaction_id,
        user_id=current_user.id
    )
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return TransactionResponse.model_validate(transaction)


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: UUID,
    update_data: TransactionUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update transaction details.
    
    Allows updating:
    - user_category: Custom category override
    - user_notes: Personal notes about the transaction
    - is_excluded: Exclude from budgets and statistics
    """
    transaction_service = TransactionService(db)
    transaction = await transaction_service.update_transaction(
        transaction_id=transaction_id,
        user_id=current_user.id,
        update_data=update_data
    )
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return TransactionResponse.model_validate(transaction)


@router.post("/bulk-categorize")
async def bulk_categorize_transactions(
    request: BulkCategorizeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Bulk update category for multiple transactions."""
    transaction_service = TransactionService(db)
    updated_count = await transaction_service.bulk_categorize(
        transaction_ids=request.transaction_ids,
        user_id=current_user.id,
        category=request.category
    )
    
    return {
        "message": f"Successfully categorized {updated_count} transactions",
        "updated_count": updated_count
    }


@router.get("/stats/summary", response_model=TransactionStatsResponse)
async def get_transaction_statistics(
    start_date: Optional[date] = Query(None, description="Start date (defaults to 30 days ago)"),
    end_date: Optional[date] = Query(None, description="End date (defaults to today)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get transaction statistics for a date range.
    
    Returns:
    - Total income and expenses
    - Net amount (income - expenses)
    - Transaction count
    - Average transaction amount
    - Spending breakdown by category
    - Monthly trends
    """
    transaction_service = TransactionService(db)
    stats = await transaction_service.get_statistics(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    return stats
