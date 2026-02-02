from sqlalchemy import String, Text, Boolean, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any
import enum

from app.models.base import BaseModel


class InsightType(str, enum.Enum):
    """Types of insights that can be generated."""
    SAVINGS_OPPORTUNITY = "savings_opportunity"
    SPENDING_ALERT = "spending_alert"
    BUDGET_ALERT = "budget_alert"
    GOAL_PROGRESS = "goal_progress"
    GOAL_BEHIND = "goal_behind"
    PATTERN_DETECTION = "pattern_detection"
    CELEBRATION = "celebration"
    TIP = "tip"
    ANOMALY = "anomaly"
    SUBSCRIPTION_WARNING = "subscription_warning"


class InsightPriority(str, enum.Enum):
    """Priority levels for insights."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Insight(BaseModel):
    """AI-generated financial insights and nudges."""
    __tablename__ = "insights"
    
    # Foreign key
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Insight metadata
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="normal"
    )
    
    # Content
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Optional action data
    action_type: Mapped[Optional[str]] = mapped_column(String(50))  # e.g., "view_category", "review_goal"
    action_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)  # Action parameters
    
    # Context and metadata
    context_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)  # Data used to generate insight
    category: Mapped[Optional[str]] = mapped_column(String(100))  # Related category if applicable
    amount: Mapped[Optional[float]] = mapped_column()  # Related amount if applicable
    
    # Status
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_dismissed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    read_at: Mapped[Optional[datetime]] = mapped_column()
    dismissed_at: Mapped[Optional[datetime]] = mapped_column()
    
    # Expiration
    expires_at: Mapped[Optional[datetime]] = mapped_column(index=True)  # Some insights may expire
    
    # Relationship
    user: Mapped["User"] = relationship(back_populates="insights")
    
    def __repr__(self) -> str:
        return f"<Insight(id={self.id}, type={self.type}, user_id={self.user_id})>"
