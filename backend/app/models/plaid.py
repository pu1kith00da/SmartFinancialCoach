from sqlalchemy import String, DateTime, Boolean, ForeignKey, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from uuid import UUID
from typing import Optional

from app.models.base import BaseModel


class Institution(BaseModel):
    """Financial institution model."""
    __tablename__ = "institutions"
    
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Plaid data
    plaid_institution_id: Mapped[str] = mapped_column(String(100), nullable=False)
    plaid_item_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    plaid_access_token: Mapped[str] = mapped_column(Text, nullable=False)  # Encrypted
    
    # Institution info
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    logo: Mapped[Optional[str]] = mapped_column(String(500))
    primary_color: Mapped[Optional[str]] = mapped_column(String(7))
    url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    sync_cursor: Mapped[Optional[str]] = mapped_column(Text)  # For incremental sync
    
    # Error tracking
    error_code: Mapped[Optional[str]] = mapped_column(String(50))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    
    # Relationships
    accounts: Mapped[list["Account"]] = relationship(
        back_populates="institution",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Institution(id={self.id}, name={self.name}, user_id={self.user_id})>"


class Account(BaseModel):
    """Bank account model."""
    __tablename__ = "accounts"
    
    institution_id: Mapped[UUID] = mapped_column(
        ForeignKey("institutions.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Plaid data
    plaid_account_id: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    
    # Account info
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    official_name: Mapped[Optional[str]] = mapped_column(String(200))
    mask: Mapped[Optional[str]] = mapped_column(String(10))  # Last 4 digits
    
    # Account type
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # depository, credit, loan, investment
    subtype: Mapped[Optional[str]] = mapped_column(String(50))  # checking, savings, credit card, etc.
    
    # Balances
    current_balance: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    available_balance: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    limit: Mapped[Optional[float]] = mapped_column(Numeric(15, 2))
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    
    # Relationships
    institution: Mapped["Institution"] = relationship(back_populates="accounts")
    
    def __repr__(self) -> str:
        return f"<Account(id={self.id}, name={self.name}, type={self.type})>"
