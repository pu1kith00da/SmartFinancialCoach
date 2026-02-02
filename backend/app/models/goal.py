from sqlalchemy import String, Text, Boolean, ForeignKey, Enum as SQLEnum, Date, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, date as date_type
from uuid import UUID
from typing import Optional, List
import enum

from app.models.base import BaseModel


class GoalType(str, enum.Enum):
    """Types of financial goals."""
    EMERGENCY_FUND = "emergency_fund"
    DEBT_PAYOFF = "debt_payoff"
    SAVINGS = "savings"
    RETIREMENT = "retirement"
    IRREGULAR_EXPENSE = "irregular_expense"


class GoalStatus(str, enum.Enum):
    """Status of a financial goal."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class GoalPriority(str, enum.Enum):
    """Priority level for goals."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Goal(BaseModel):
    """Financial goals for users to track savings and debt payoff."""
    __tablename__ = "goals"
    
    # Foreign key
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Goal metadata
    type: Mapped[GoalType] = mapped_column(
        SQLEnum(GoalType, native_enum=False),
        nullable=False,
        index=True
    )
    status: Mapped[GoalStatus] = mapped_column(
        SQLEnum(GoalStatus, native_enum=False),
        nullable=False,
        default=GoalStatus.ACTIVE,
        index=True
    )
    priority: Mapped[GoalPriority] = mapped_column(
        SQLEnum(GoalPriority, native_enum=False),
        nullable=False,
        default=GoalPriority.MEDIUM
    )
    
    # Goal details
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    target_amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    current_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0, nullable=False)
    reserved_amount: Mapped[float] = mapped_column(Numeric(15, 2), default=0.0, nullable=False)  # Funds reserved from cash management
    
    # Dates
    target_date: Mapped[Optional[date_type]] = mapped_column(Date, nullable=True)
    started_at: Mapped[date_type] = mapped_column(Date, nullable=False, default=date_type.today)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    
    # Visual & motivation
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)  # Hex color
    
    # Contribution settings
    monthly_target: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    auto_contribute: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    auto_contribute_amount: Mapped[Optional[float]] = mapped_column(Numeric(15, 2), nullable=True)
    auto_contribute_day: Mapped[Optional[int]] = mapped_column(nullable=True)  # Day of month (1-31)
    
    # Round-up savings
    enable_roundup: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # For debt payoff goals
    debt_account_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("accounts.id", ondelete="SET NULL"),
        nullable=True
    )
    interest_rate: Mapped[Optional[float]] = mapped_column(nullable=True)  # Annual percentage
    
    # Calculated/cached fields
    projected_completion_date: Mapped[Optional[date_type]] = mapped_column(Date, nullable=True)
    is_on_track: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="goals")
    contributions: Mapped[List["GoalContribution"]] = relationship(
        back_populates="goal",
        cascade="all, delete-orphan",
        order_by="GoalContribution.contributed_at.desc()"
    )
    
    def __repr__(self) -> str:
        return f"<Goal(id={self.id}, name={self.name}, type={self.type}, progress={self.progress_percentage}%)>"
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.target_amount <= 0:
            return 0.0
        return min(100.0, (self.current_amount / self.target_amount) * 100)
    
    @property
    def remaining_amount(self) -> float:
        """Calculate remaining amount to reach goal."""
        return max(0.0, self.target_amount - self.current_amount)


class GoalContribution(BaseModel):
    """Track contributions made toward goals."""
    __tablename__ = "goal_contributions"
    
    # Foreign keys
    goal_id: Mapped[UUID] = mapped_column(
        ForeignKey("goals.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Contribution details
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    contributed_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow)
    
    # Optional: Link to transaction if contribution came from income
    transaction_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("transactions.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Contribution source
    source: Mapped[str] = mapped_column(String(50), default="manual", nullable=False)  # manual, auto, roundup, windfall
    
    # Relationships
    goal: Mapped["Goal"] = relationship(back_populates="contributions")
    user: Mapped["User"] = relationship()
    
    def __repr__(self) -> str:
        return f"<GoalContribution(id={self.id}, goal_id={self.goal_id}, amount={self.amount})>"
