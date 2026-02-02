from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# Link Token Schemas
class LinkTokenRequest(BaseModel):
    """Request to create a Plaid Link token."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "redirect_uri": "https://app.example.com/oauth-redirect",
                "webhook_url": "https://api.example.com/webhooks/plaid"
            }
        }
    )
    
    redirect_uri: Optional[str] = Field(None, description="OAuth redirect URI")
    webhook_url: Optional[str] = Field(None, description="Webhook URL for account updates")


class LinkTokenResponse(BaseModel):
    """Response containing Plaid Link token."""
    link_token: str
    expiration: datetime


# Public Token Exchange Schemas
class PublicTokenExchangeRequest(BaseModel):
    """Request to exchange public token for access token."""
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "public_token": "public-sandbox-8ab976e6-64bc-4b38-98f7-231e99d2d48e"
            }
        }
    )
    
    public_token: str = Field(..., description="Public token from Plaid Link", examples=["public-sandbox-8ab976e6-64bc-4b38-98f7-231e99d2d48e"])


class PublicTokenExchangeResponse(BaseModel):
    """Response after exchanging public token."""
    institution_id: UUID
    accounts_added: int


# Institution Schemas
class InstitutionResponse(BaseModel):
    """Institution information."""
    id: UUID
    name: str
    logo: Optional[str] = None
    primary_color: Optional[str] = None
    is_active: bool
    last_synced_at: Optional[datetime] = None
    accounts_count: int = 0
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Account Schemas
class AccountBalance(BaseModel):
    """Account balance information."""
    current: Optional[float] = None
    available: Optional[float] = None
    limit: Optional[float] = None
    currency_code: str = "USD"


class AccountResponse(BaseModel):
    """Account information."""
    id: UUID
    institution_id: UUID
    name: str
    official_name: Optional[str] = None
    mask: Optional[str] = None
    type: str
    subtype: Optional[str] = None
    balance: AccountBalance
    is_active: bool
    last_synced_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_account(cls, account: 'Account') -> 'AccountResponse':
        """Create AccountResponse from Account model."""
        try:
            return cls(
                id=account.id,
                institution_id=account.institution_id,
                name=account.name or '',
                official_name=account.official_name,
                mask=account.mask,
                type=account.type or '',
                subtype=account.subtype,
                balance=AccountBalance(
                    current=float(account.current_balance) if account.current_balance is not None else None,
                    available=float(account.available_balance) if account.available_balance is not None else None,
                    limit=float(account.limit) if account.limit is not None else None,
                    currency_code=account.currency or 'USD'
                ),
                is_active=bool(account.is_active),
                last_synced_at=account.last_synced_at,
                created_at=account.created_at,
                updated_at=account.updated_at
            )
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating AccountResponse from account {account.id}: {str(e)}")
            raise

    class Config:
        from_attributes = True


class AccountListResponse(BaseModel):
    """List of accounts."""
    accounts: List[AccountResponse]
    total: int


# Sync Schemas
class SyncRequest(BaseModel):
    """Request to sync institution data."""
    institution_id: UUID


class SyncResponse(BaseModel):
    """Response after syncing institution data."""
    institution_id: UUID
    accounts_updated: int
    transactions_added: int
    last_synced_at: datetime
    success: bool
    message: Optional[str] = None


# Institution Management
class InstitutionUpdateRequest(BaseModel):
    """Request to update institution."""
    is_active: Optional[bool] = None


class RemoveInstitutionRequest(BaseModel):
    """Request to remove an institution."""
    institution_id: UUID
