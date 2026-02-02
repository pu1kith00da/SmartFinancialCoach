from sqlalchemy import String, Numeric, Date, Text, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING
from datetime import date, datetime
from uuid import UUID
import enum

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.account import Account


class BillFrequency(str, enum.Enum):
    """Bill payment frequency."""
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    SEMI_ANNUALLY = "semi_annually"
    ANNUALLY = "annually"
    ONE_TIME = "one_time"


class BillStatus(str, enum.Enum):
    """Bill payment status."""
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"


class BillCategory(str, enum.Enum):
    """Bill categories."""
    HOUSING = "housing"          # Rent, mortgage, property tax
    UTILITIES = "utilities"      # Electric, gas, water, trash
    INSURANCE = "insurance"      # Auto, health, life, home
    TRANSPORTATION = "transportation"  # Car payment, gas, parking
    COMMUNICATION = "communication"    # Phone, internet, cable
    HEALTHCARE = "healthcare"    # Medical bills, prescriptions
    EDUCATION = "education"      # Student loans, tuition
    PERSONAL = "personal"        # Credit cards, personal loans
    ENTERTAINMENT = "entertainment"    # Subscriptions, memberships
    PROFESSIONAL = "professional"     # Licenses, memberships
    OTHER = "other"


class Bill(BaseModel):
    """
    Recurring bills and one-time payments.
    Can be manually added or auto-detected from transactions.
    """
    __tablename__ = "bills"
    
    # Foreign keys
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)  # Account to pay from
    
    # Bill details
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    payee: Mapped[str] = mapped_column(String(200), nullable=False)  # Who to pay
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Amount information
    amount: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)  # Can be variable
    estimated_amount: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    min_amount: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    max_amount: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    is_variable_amount: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Frequency and dates
    frequency: Mapped[str] = mapped_column(String(20), nullable=False)
    first_due_date: Mapped[date] = mapped_column(Date, nullable=False)
    next_due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    last_paid_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    last_paid_amount: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    
    # Payment settings
    autopay_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    autopay_account_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)
    reminder_days_before: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default=BillStatus.PENDING.value, nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Detection and tracking
    auto_detected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    confirmed_by_user: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Additional details
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    account_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Encrypted/masked
    
    # Contact information
    payee_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    payee_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    payee_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Visual
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="bills")
    account: Mapped[Optional["Account"]] = relationship(foreign_keys="[Bill.account_id]")
    
    def __repr__(self) -> str:
        return f"<Bill(id={self.id}, name={self.name}, payee={self.payee}, amount={self.amount})>"
    
    @property
    def monthly_amount(self) -> float:
        """Calculate monthly cost based on frequency."""
        amount = float(self.amount or self.estimated_amount or 0)
        
        if self.frequency == BillFrequency.WEEKLY.value:
            return amount * 4.33
        elif self.frequency == BillFrequency.BIWEEKLY.value:
            return amount * 2.17
        elif self.frequency == BillFrequency.MONTHLY.value:
            return amount
        elif self.frequency == BillFrequency.QUARTERLY.value:
            return amount / 3
        elif self.frequency == BillFrequency.SEMI_ANNUALLY.value:
            return amount / 6
        elif self.frequency == BillFrequency.ANNUALLY.value:
            return amount / 12
        elif self.frequency == BillFrequency.ONE_TIME.value:
            return 0  # Don't include one-time bills in monthly calculations
        return amount
    
    @property
    def annual_amount(self) -> float:
        """Calculate annual cost."""
        return self.monthly_amount * 12
    
    @property
    def days_until_due(self) -> int:
        """Calculate days until next due date."""
        delta = self.next_due_date - date.today()
        return max(0, delta.days)
    
    @property
    def is_due_soon(self) -> bool:
        """Check if bill is due within reminder window."""
        return self.days_until_due <= self.reminder_days_before
    
    @property
    def is_overdue(self) -> bool:
        """Check if bill is overdue."""
        return self.next_due_date < date.today() and self.status != BillStatus.PAID.value
    
    def get_next_due_date_after(self, after_date: date) -> date:
        """Calculate the next due date after a given date based on frequency."""
        from dateutil.relativedelta import relativedelta
        
        if self.frequency == BillFrequency.WEEKLY.value:
            delta = relativedelta(weeks=1)
        elif self.frequency == BillFrequency.BIWEEKLY.value:
            delta = relativedelta(weeks=2)
        elif self.frequency == BillFrequency.MONTHLY.value:
            delta = relativedelta(months=1)
        elif self.frequency == BillFrequency.QUARTERLY.value:
            delta = relativedelta(months=3)
        elif self.frequency == BillFrequency.SEMI_ANNUALLY.value:
            delta = relativedelta(months=6)
        elif self.frequency == BillFrequency.ANNUALLY.value:
            delta = relativedelta(years=1)
        else:  # ONE_TIME
            return after_date
        
        next_date = self.next_due_date
        while next_date <= after_date:
            next_date += delta
        
        return next_date


class BillPayment(BaseModel):
    """
    Track actual bill payments.
    Links to transactions when bills are paid.
    """
    __tablename__ = "bill_payments"
    
    # Foreign keys
    bill_id: Mapped[UUID] = mapped_column(ForeignKey("bills.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_id: Mapped[Optional[UUID]] = mapped_column(nullable=True)  # Link to actual transaction
    
    # Payment details
    amount_paid: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    payment_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)  # Original due date for this payment
    
    # Payment method
    payment_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # online, check, auto, etc.
    confirmation_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="completed", nullable=False)
    is_late: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Additional details
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    bill: Mapped["Bill"] = relationship()
    user: Mapped["User"] = relationship()
    
    def __repr__(self) -> str:
        return f"<BillPayment(id={self.id}, bill_id={self.bill_id}, amount={self.amount_paid})>"
    
    @property
    def days_late(self) -> int:
        """Calculate how many days late the payment was."""
        if self.payment_date > self.due_date:
            return (self.payment_date - self.due_date).days
        return 0