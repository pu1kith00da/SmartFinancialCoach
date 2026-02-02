from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, extract
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from uuid import UUID
import logging
import json

from app.models.transaction import Transaction, TransactionCategory, TransactionType, TransactionStatus
from app.models.plaid import Account
from app.schemas.transaction import (
    TransactionFilterRequest,
    TransactionUpdateRequest,
    TransactionStatsResponse,
    CategorySpending
)

logger = logging.getLogger(__name__)


class TransactionService:
    """Service for transaction operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # Category mapping based on Plaid's categories
    CATEGORY_MAPPING = {
        "Food and Drink": "Food & Dining",
        "Restaurants": "Food & Dining",
        "Fast Food": "Food & Dining",
        "Coffee Shop": "Food & Dining",
        "Groceries": "Groceries",
        "Transfer": "Transfer",
        "Payment": "Payment",
        "Transportation": "Transportation",
        "Gas": "Transportation",
        "Public Transportation": "Transportation",
        "Ride Share": "Transportation",
        "Shopping": "Shopping",
        "Recreation": "Entertainment",
        "Entertainment": "Entertainment",
        "Travel": "Travel",
        "Healthcare": "Healthcare",
        "Bills": "Bills & Utilities",
        "Utilities": "Bills & Utilities",
        "Rent": "Housing",
        "Mortgage": "Housing",
        "Income": "Income",
        "Paycheck": "Income",
    }
    
    async def create_transaction(
        self,
        user_id: UUID,
        account_id: UUID,
        plaid_data: Dict[str, Any]
    ) -> Transaction:
        """Create a transaction from Plaid data."""
        try:
            # Extract Plaid categories
            plaid_categories = plaid_data.get('category', [])
            primary_category = plaid_categories[0] if plaid_categories else None
            
            # Map to our category system
            category = self._map_category(primary_category) if primary_category else "Other"
            
            # Determine transaction type
            amount = plaid_data['amount']
            tx_type = TransactionType.DEBIT if amount > 0 else TransactionType.CREDIT
            
            # Parse dates - handle both string and date objects
            transaction_date = plaid_data['date']
            if isinstance(transaction_date, str):
                transaction_date = datetime.strptime(transaction_date, '%Y-%m-%d').date()
            
            authorized_date = plaid_data.get('authorized_date')
            if authorized_date:
                if isinstance(authorized_date, str):
                    authorized_date = datetime.strptime(authorized_date, '%Y-%m-%d').date()
            
            # Create transaction
            transaction = Transaction(
                user_id=user_id,
                account_id=account_id,
                plaid_transaction_id=plaid_data['transaction_id'],
                date=transaction_date,
                authorized_date=authorized_date,
                name=plaid_data['name'],
                merchant_name=plaid_data.get('merchant_name'),
                amount=abs(amount),
                currency=plaid_data.get('iso_currency_code', 'USD'),
                type=tx_type,
                status=TransactionStatus.PENDING if plaid_data.get('pending', False) 
                    else TransactionStatus.POSTED,
                category=category,
                category_detailed=plaid_categories[-1] if plaid_categories else None,
                plaid_category=json.dumps(plaid_categories),
                location_address=plaid_data.get('location', {}).get('address'),
                location_city=plaid_data.get('location', {}).get('city'),
                location_region=plaid_data.get('location', {}).get('region'),
                location_country=plaid_data.get('location', {}).get('country'),
                payment_channel=plaid_data.get('payment_channel'),
                pending_transaction_id=plaid_data.get('pending_transaction_id')
            )
            
            self.db.add(transaction)
            await self.db.flush()
            
            # Detect if recurring
            await self._detect_recurring(transaction)
            
            return transaction
            
        except Exception as e:
            logger.error(f"Error creating transaction: {str(e)}")
            raise
    
    async def create_manual_transaction(
        self,
        user_id: UUID,
        name: str,
        amount: float,
        category: str,
        transaction_date: date,
        transaction_type: str = "cash",
        notes: Optional[str] = None
    ) -> Transaction:
        """Create a manual transaction for cash or planned expenses only."""
        try:
            # Determine transaction type (debit for expenses, credit for income)
            tx_type = TransactionType.DEBIT if amount < 0 else TransactionType.CREDIT
            
            # Create transaction with clear manual marking
            transaction = Transaction(
                user_id=user_id,
                account_id=None,  # No account for manual transactions
                name=name,
                amount=abs(amount),
                currency='USD',
                type=tx_type,
                status=TransactionStatus.POSTED,
                category=category,
                user_category=category,
                user_notes=notes,
                date=transaction_date,
                payment_channel='manual',
                merchant_name=f"Manual ({transaction_type})",  # Mark as manual
                plaid_transaction_id=None  # Explicitly no Plaid ID
            )
            
            self.db.add(transaction)
            await self.db.flush()
            
            return transaction
            
        except Exception as e:
            logger.error(f"Error creating manual transaction: {str(e)}")
            raise
    
    def _map_category(self, plaid_category: str) -> str:
        """Map Plaid category to our category system."""
        for key, value in self.CATEGORY_MAPPING.items():
            if key.lower() in plaid_category.lower():
                return value
        return "Other"
    
    async def _detect_recurring(self, transaction: Transaction) -> None:
        """Detect if transaction is recurring."""
        # Look for similar transactions in past 90 days
        past_date = transaction.date - timedelta(days=90)
        
        result = await self.db.execute(
            select(Transaction).where(
                and_(
                    Transaction.user_id == transaction.user_id,
                    Transaction.merchant_name == transaction.merchant_name,
                    Transaction.amount == transaction.amount,
                    Transaction.date >= past_date,
                    Transaction.date < transaction.date,
                    Transaction.id != transaction.id
                )
            )
        )
        similar_transactions = result.scalars().all()
        
        if len(similar_transactions) >= 2:
            transaction.is_recurring = True
            # Simple frequency detection
            if len(similar_transactions) >= 3:
                transaction.recurring_frequency = "monthly"
            else:
                transaction.recurring_frequency = "occasional"
    
    async def get_transactions(
        self,
        user_id: UUID,
        filters: TransactionFilterRequest
    ) -> tuple[List[Transaction], int]:
        """Get transactions with filters and pagination."""
        # Build query
        query = select(Transaction).where(Transaction.user_id == user_id)
        
        # Apply filters
        if filters.account_ids:
            query = query.where(Transaction.account_id.in_(filters.account_ids))
        
        if filters.category:
            query = query.where(
                or_(
                    Transaction.category == filters.category,
                    Transaction.user_category == filters.category
                )
            )
        
        if filters.start_date:
            query = query.where(Transaction.date >= filters.start_date)
        
        if filters.end_date:
            query = query.where(Transaction.date <= filters.end_date)
        
        if filters.min_amount is not None:
            query = query.where(Transaction.amount >= filters.min_amount)
        
        if filters.max_amount is not None:
            query = query.where(Transaction.amount <= filters.max_amount)
        
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    Transaction.name.ilike(search_term),
                    Transaction.merchant_name.ilike(search_term)
                )
            )
        
        if filters.type:
            query = query.where(Transaction.type == filters.type)
        
        if filters.status:
            query = query.where(Transaction.status == filters.status)
        
        if filters.is_recurring is not None:
            query = query.where(Transaction.is_recurring == filters.is_recurring)
        
        if filters.is_excluded is not None:
            query = query.where(Transaction.is_excluded == filters.is_excluded)
        
        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply sorting and pagination
        query = query.order_by(Transaction.date.desc(), Transaction.created_at.desc())
        query = query.limit(filters.limit).offset(filters.offset)
        
        # Execute query
        result = await self.db.execute(query)
        transactions = list(result.scalars().all())
        
        return transactions, total
    
    async def get_transaction(self, transaction_id: UUID, user_id: UUID) -> Optional[Transaction]:
        """Get a single transaction."""
        result = await self.db.execute(
            select(Transaction).where(
                and_(
                    Transaction.id == transaction_id,
                    Transaction.user_id == user_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def update_transaction(
        self,
        transaction_id: UUID,
        user_id: UUID,
        update_data: TransactionUpdateRequest
    ) -> Optional[Transaction]:
        """Update transaction details."""
        transaction = await self.get_transaction(transaction_id, user_id)
        if not transaction:
            return None
        
        if update_data.user_category is not None:
            transaction.user_category = update_data.user_category
        
        if update_data.user_notes is not None:
            transaction.user_notes = update_data.user_notes
        
        if update_data.is_excluded is not None:
            transaction.is_excluded = update_data.is_excluded
        
        await self.db.commit()
        await self.db.refresh(transaction)
        
        return transaction
    
    async def bulk_categorize(
        self,
        transaction_ids: List[UUID],
        user_id: UUID,
        category: str
    ) -> int:
        """Bulk update category for multiple transactions."""
        result = await self.db.execute(
            select(Transaction).where(
                and_(
                    Transaction.id.in_(transaction_ids),
                    Transaction.user_id == user_id
                )
            )
        )
        transactions = result.scalars().all()
        
        for transaction in transactions:
            transaction.user_category = category
        
        await self.db.commit()
        return len(transactions)
    
    async def get_statistics(
        self,
        user_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> TransactionStatsResponse:
        """Get transaction statistics."""
        # Default to last 30 days
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Get transactions in date range
        result = await self.db.execute(
            select(Transaction).where(
                and_(
                    Transaction.user_id == user_id,
                    Transaction.date >= start_date,
                    Transaction.date <= end_date,
                    Transaction.is_excluded == False
                )
            )
        )
        transactions = result.scalars().all()
        
        # Calculate stats
        total_count = len(transactions)
        total_income = sum(t.amount for t in transactions if t.type == TransactionType.CREDIT)
        total_expenses = sum(t.amount for t in transactions if t.type == TransactionType.DEBIT)
        net_amount = total_income - total_expenses
        average_transaction = (total_income + total_expenses) / total_count if total_count > 0 else 0
        
        # Category breakdown
        categories_breakdown = {}
        for t in transactions:
            category = t.user_category or t.category or "Uncategorized"
            if category not in categories_breakdown:
                categories_breakdown[category] = 0
            if t.type == TransactionType.DEBIT:
                categories_breakdown[category] += float(t.amount)
        
        # Monthly trend (simplified for now)
        monthly_trend = {}
        
        return TransactionStatsResponse(
            total_count=total_count,
            total_income=float(total_income),
            total_expenses=float(total_expenses),
            net_amount=float(net_amount),
            average_transaction=float(average_transaction),
            categories_breakdown=categories_breakdown,
            monthly_trend=monthly_trend
        )
