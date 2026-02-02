from sqlalchemy import String, Numeric, Date, Text, Boolean, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, TYPE_CHECKING
from datetime import date, datetime
from uuid import UUID
import enum

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.transaction import Transaction


class SubscriptionStatus(str, enum.Enum):
    """Subscription status."""
    ACTIVE = "active"
    CANCELLED = "cancelled"
    PAUSED = "paused"
    FREE_TRIAL = "free_trial"
    EXPIRED = "expired"


class BillingCycle(str, enum.Enum):
    """Subscription billing cycle."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class DetectionConfidence(str, enum.Enum):
    """Detection confidence level."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Subscription(BaseModel):
    """
    Detected recurring subscriptions and charges.
    Auto-detected from transaction patterns or manually added.
    """
    __tablename__ = "subscriptions"
    
    # Foreign keys
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Subscription details
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    service_provider: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Billing information
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    billing_cycle: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Dates
    first_charge_date: Mapped[date] = mapped_column(Date, nullable=False)
    next_billing_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    last_charge_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Charge tracking
    last_charge_amount: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    total_charges: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    average_amount: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False, index=True)
    
    # Trial tracking
    is_trial: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    trial_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Additional details
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    cancellation_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Visual
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    
    # Detection information
    detection_confidence: Mapped[str] = mapped_column(String(20), default="manual", nullable=False)
    auto_detected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    confirmed_by_user: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="subscriptions")
    
    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, name={self.name}, amount={self.amount}, cycle={self.billing_cycle})>"
    
    @property
    def monthly_cost(self) -> float:
        """Calculate monthly cost regardless of billing cycle."""
        if self.billing_cycle == BillingCycle.DAILY.value:
            return float(self.amount) * 30
        elif self.billing_cycle == BillingCycle.WEEKLY.value:
            return float(self.amount) * 4.33
        elif self.billing_cycle == BillingCycle.MONTHLY.value:
            return float(self.amount)
        elif self.billing_cycle == BillingCycle.QUARTERLY.value:
            return float(self.amount) / 3
        elif self.billing_cycle == BillingCycle.YEARLY.value:
            return float(self.amount) / 12
        return float(self.amount)
    
    @property
    def annual_cost(self) -> float:
        """Calculate annual cost."""
        return self.monthly_cost * 12
    
    @property
    def days_until_next_billing(self) -> int:
        """Calculate days until next billing."""
        delta = self.next_billing_date - date.today()
        return max(0, delta.days)
    
    @property
    def is_trial_ending_soon(self) -> bool:
        """Check if free trial is ending within 7 days."""
        if not self.is_trial or not self.trial_end_date:
            return False
        days_left = (self.trial_end_date - date.today()).days
        return 0 <= days_left <= 7
