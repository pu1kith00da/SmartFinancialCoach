from sqlalchemy import String, DateTime, Boolean, ForeignKey, Text, Numeric, Enum as SQLEnum, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from datetime import date as date_type
from uuid import UUID
from typing import Optional
import enum

from app.models.base import BaseModel


class TransactionType(str, enum.Enum):
    """Transaction type enumeration."""
    DEBIT = "debit"
    CREDIT = "credit"


class TransactionStatus(str, enum.Enum):
    """Transaction status enumeration."""
    PENDING = "pending"
    POSTED = "posted"


class Transaction(BaseModel):
    """Transaction model for financial transactions."""
    __tablename__ = "transactions"
    
    # Foreign keys
    account_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), 
        nullable=True, 
        index=True
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Plaid data
    plaid_transaction_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, unique=True)
    
    # Transaction details
    date: Mapped[date_type] = mapped_column(Date, nullable=False, index=True)
    authorized_date: Mapped[Optional[date_type]] = mapped_column(Date, nullable=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    merchant_name: Mapped[Optional[str]] = mapped_column(String(200))
    
    # Amounts
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    
    # Type and status
    type: Mapped[TransactionType] = mapped_column(
        SQLEnum(TransactionType, native_enum=False),
        nullable=False,
        index=True
    )
    status: Mapped[TransactionStatus] = mapped_column(
        SQLEnum(TransactionStatus, native_enum=False),
        nullable=False,
        default=TransactionStatus.POSTED
    )
    
    # Categorization
    category: Mapped[Optional[str]] = mapped_column(String(100), index=True)  # Primary category
    category_detailed: Mapped[Optional[str]] = mapped_column(String(200))  # Detailed subcategory
    plaid_category: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Original Plaid category array as JSON
    
    # User customization
    user_category: Mapped[Optional[str]] = mapped_column(String(100))  # User-defined override
    user_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_excluded: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # Exclude from budgets
    
    # Additional metadata
    location_address: Mapped[Optional[str]] = mapped_column(String(500))
    location_city: Mapped[Optional[str]] = mapped_column(String(100))
    location_region: Mapped[Optional[str]] = mapped_column(String(100))
    location_country: Mapped[Optional[str]] = mapped_column(String(2))
    payment_channel: Mapped[Optional[str]] = mapped_column(String(50))  # online, in store, other
    
    # Pending transaction tracking
    pending_transaction_id: Mapped[Optional[str]] = mapped_column(String(100))
    
    # AI insights
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    recurring_frequency: Mapped[Optional[str]] = mapped_column(String(50))  # monthly, weekly, etc.
    
    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, name={self.name}, amount={self.amount}, date={self.date})>"


class TransactionCategory(BaseModel):
    """Custom transaction categories defined by user."""
    __tablename__ = "transaction_categories"
    
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    parent_category: Mapped[Optional[str]] = mapped_column(String(100))
    icon: Mapped[Optional[str]] = mapped_column(String(50))
    color: Mapped[Optional[str]] = mapped_column(String(7))  # Hex color
    
    # Budget association
    monthly_budget: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    
    # Category rules for auto-assignment
    keywords: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of keywords
    merchant_patterns: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of patterns
    
    def __repr__(self) -> str:
        return f"<TransactionCategory(id={self.id}, name={self.name})>"
