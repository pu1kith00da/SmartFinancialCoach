"""
Analytics models for tracking financial metrics over time.
"""
from sqlalchemy import Column, ForeignKey, Numeric, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from uuid import UUID as UUID_TYPE
from typing import Optional, Dict, Any

from app.models.base import BaseModel


class NetWorthSnapshot(BaseModel):
    """Historical snapshots of user's net worth."""
    __tablename__ = "net_worth_snapshots"
    
    # Foreign key
    user_id: Mapped[UUID_TYPE] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Net worth components
    total_assets: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    total_liabilities: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    net_worth: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    
    # Asset breakdown
    liquid_assets: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))  # Cash, checking, savings
    investment_assets: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))  # Stocks, bonds, crypto
    fixed_assets: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))  # Real estate, vehicles
    other_assets: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    
    # Liability breakdown
    credit_card_debt: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    student_loans: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    mortgage_debt: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    auto_loans: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    other_debt: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    
    # Metadata
    snapshot_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    notes: Mapped[Optional[str]] = mapped_column()
    breakdown_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)  # Additional breakdown details
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="net_worth_snapshots")
    
    @property
    def debt_to_asset_ratio(self) -> float:
        """Calculate debt-to-asset ratio."""
        if self.total_assets == 0:
            return 0.0
        return float(self.total_liabilities / self.total_assets)
    
    @property
    def liquid_ratio(self) -> float:
        """Calculate percentage of assets that are liquid."""
        if self.total_assets == 0:
            return 0.0
        return float((self.liquid_assets or 0) / self.total_assets)
    
    def __repr__(self) -> str:
        return f"<NetWorthSnapshot(user_id={self.user_id}, date={self.snapshot_date}, net_worth={self.net_worth})>"
