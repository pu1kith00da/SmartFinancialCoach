# Smart Financial Coach - AI Agent Implementation Guide

> **Purpose:** This document serves as a focused implementation guide for an AI coding agent to build the Smart Financial Coach application. It contains specific instructions, code patterns, and implementation details.

---

## Quick Start Commands

```bash
# Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend Setup
cd frontend
npm install
npm run dev

# Run with Docker
docker-compose up -d
```

---

## 1. Backend Implementation Guide

### 1.1 Project Initialization

```bash
# Create backend structure
mkdir -p backend/app/{api/v1,core,models,schemas,repositories,services,ai_engine/prompts,tasks}
mkdir -p backend/{tests/{unit,integration,factories},migrations/versions,scripts}

# Initialize Python project
cd backend
python -m venv venv
source venv/bin/activate
```

### 1.2 Requirements (requirements.txt)

```txt
# Core Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0

# Database
sqlalchemy[asyncio]==2.0.25
asyncpg==0.29.0
alembic==1.13.1
greenlet==3.0.3

# Authentication & Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pyotp==2.9.0  # For MFA

# Redis & Caching
redis==5.0.1
aioredis==2.0.1

# Background Tasks
celery==5.3.6

# Plaid Integration
plaid-python==16.0.0

# AI/ML
openai==1.9.0
anthropic==0.18.0
scikit-learn==1.4.0
prophet==1.1.5
pandas==2.1.4
numpy==1.26.3

# Utilities
httpx==0.26.0
python-dateutil==2.8.2
tenacity==8.2.3  # Retry logic

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
pytest-cov==4.1.0
httpx==0.26.0
factory-boy==3.3.0

# Code Quality
black==24.1.0
isort==5.13.2
flake8==7.0.0
mypy==1.8.0
```

### 1.3 Application Configuration (app/config.py)

```python
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Smart Financial Coach"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_MIN_LENGTH: int = 12
    
    # Plaid
    PLAID_CLIENT_ID: str
    PLAID_SECRET: str
    PLAID_ENV: str = "sandbox"  # sandbox, development, production
    PLAID_PRODUCTS: list = ["transactions", "auth", "identity"]
    PLAID_COUNTRY_CODES: list = ["US"]
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    AI_MODEL: str = "gpt-4"  # or "claude-3-opus"
    
    # Email
    SENDGRID_API_KEY: Optional[str] = None
    FROM_EMAIL: str = "noreply@fincoach.app"
    
    # Feature Flags
    ENABLE_MFA: bool = True
    ENABLE_GAMIFICATION: bool = True
    MAX_INSIGHTS_PER_DAY: int = 2
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

### 1.4 Database Setup (app/core/database.py)

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DEBUG,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### 1.5 Base Model (app/models/base.py)

```python
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### 1.6 User Model (app/models/user.py)

```python
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    timezone = Column(String(50), default="America/New_York")
    
    last_login_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255))
    onboarding_completed = Column(Boolean, default=False)
    subscription_tier = Column(String(20), default="free")
    
    # Relationships
    preferences = relationship("UserPreferences", back_populates="user", uselist=False)
    accounts = relationship("Account", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")
    budgets = relationship("Budget", back_populates="user")
    goals = relationship("Goal", back_populates="user")
    insights = relationship("Insight", back_populates="user")

class UserPreferences(BaseModel):
    __tablename__ = "user_preferences"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    theme = Column(String(20), default="system")
    currency = Column(String(3), default="USD")
    date_format = Column(String(20), default="MM/DD/YYYY")
    week_start = Column(String(10), default="sunday")
    fiscal_month_start = Column(Integer, default=1)
    privacy_mode = Column(Boolean, default=False)
    coaching_tone = Column(String(20), default="encouraging")
    insight_frequency = Column(String(20), default="daily")
    notification_email = Column(Boolean, default=True)
    notification_push = Column(Boolean, default=True)
    notification_sms = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="preferences")
```

### 1.7 Transaction Model (app/models/transaction.py)

```python
from sqlalchemy import Column, String, Boolean, Date, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from app.models.base import BaseModel

class Transaction(BaseModel):
    __tablename__ = "transactions"
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    plaid_transaction_id = Column(String(255), unique=True)
    
    amount = Column(Numeric(15, 2), nullable=False)  # Positive = expense
    date = Column(Date, nullable=False, index=True)
    datetime = Column(DateTime(timezone=True))
    
    name = Column(String(500), nullable=False)  # Original name
    merchant_name = Column(String(255))  # Cleaned name
    merchant_logo_url = Column(String(500))
    
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    subcategory = Column(String(100))
    
    pending = Column(Boolean, default=False)
    transaction_type = Column(String(20))  # debit, credit
    payment_channel = Column(String(20))  # online, in_store
    location = Column(JSONB)  # {city, region, country, lat, lon}
    
    notes = Column(Text)
    tags = Column(ARRAY(String(100)))
    
    is_recurring = Column(Boolean, default=False)
    is_subscription = Column(Boolean, default=False)
    is_discretionary = Column(Boolean)
    is_excluded = Column(Boolean, default=False)
    is_transfer = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")
    category = relationship("Category")
```

### 1.8 Authentication Schema (app/schemas/auth.py)

```python
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
import re

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=12)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    mfa_code: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenPayload(BaseModel):
    sub: str  # user_id
    exp: datetime
    type: str  # access or refresh

class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=12)
```

### 1.9 Security Utils (app/core/security.py)

```python
from datetime import datetime, timedelta
from typing import Optional, Union
from uuid import UUID

from jose import jwt, JWTError
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import pyotp
import secrets

from app.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Field-level encryption for sensitive data
_fernet = None
def get_fernet():
    global _fernet
    if _fernet is None:
        _fernet = Fernet(settings.SECRET_KEY[:32].encode().ljust(32, b'='))
    return _fernet

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: Union[str, UUID], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def create_refresh_token(user_id: Union[str, UUID]) -> str:
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
        "jti": secrets.token_urlsafe(32)  # Unique token ID for revocation
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None

def encrypt_sensitive_data(data: str) -> str:
    return get_fernet().encrypt(data.encode()).decode()

def decrypt_sensitive_data(encrypted_data: str) -> str:
    return get_fernet().decrypt(encrypted_data.encode()).decode()

def generate_mfa_secret() -> str:
    return pyotp.random_base32()

def verify_mfa_code(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(code)

def get_mfa_provisioning_uri(secret: str, email: str) -> str:
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=settings.APP_NAME)
```

### 1.10 Auth Endpoints (app/api/v1/auth.py)

```python
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from app.core.database import get_db
from app.core.security import (
    hash_password, verify_password, 
    create_access_token, create_refresh_token,
    decode_token, verify_mfa_code
)
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, PasswordReset
from app.services.auth_service import AuthService
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user account."""
    auth_service = AuthService(db)
    
    # Check if user exists
    existing_user = await auth_service.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = await auth_service.create_user(user_data)
    
    # Send verification email
    background_tasks.add_task(auth_service.send_verification_email, user)
    
    # Generate tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    mfa_code: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Authenticate user and return tokens."""
    auth_service = AuthService(db)
    
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check MFA if enabled
    if user.mfa_enabled:
        if not mfa_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="MFA code required"
            )
        if not verify_mfa_code(user.mfa_secret, mfa_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid MFA code"
            )
    
    # Update last login
    await auth_service.update_last_login(user.id)
    
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token."""
    payload = decode_token(refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    auth_service = AuthService(db)
    
    # Verify token not revoked
    if await auth_service.is_token_revoked(payload.get("jti")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )
    
    user_id = payload.get("sub")
    new_access_token = create_access_token(user_id)
    new_refresh_token = create_refresh_token(user_id)
    
    # Revoke old refresh token
    await auth_service.revoke_token(payload.get("jti"))
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/logout")
async def logout(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Logout user and revoke tokens."""
    auth_service = AuthService(db)
    payload = decode_token(token)
    
    if payload:
        await auth_service.revoke_all_user_tokens(payload.get("sub"))
    
    return {"message": "Successfully logged out"}

# Dependency to get current user
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    """Dependency to get the current authenticated user."""
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user_service = UserService(db)
    user = await user_service.get_by_id(payload.get("sub"))
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return user

CurrentUser = Annotated[User, Depends(get_current_user)]
```

### 1.11 Plaid Service (app/services/plaid_service.py)

```python
from typing import List, Optional
from datetime import datetime, timedelta
import plaid
from plaid.api import plaid_api
from plaid.model import (
    LinkTokenCreateRequest, LinkTokenCreateRequestUser,
    ItemPublicTokenExchangeRequest, TransactionsSyncRequest,
    AccountsGetRequest, Products, CountryCode
)

from app.config import get_settings
from app.core.security import encrypt_sensitive_data, decrypt_sensitive_data

settings = get_settings()

class PlaidService:
    def __init__(self):
        configuration = plaid.Configuration(
            host=self._get_host(),
            api_key={
                'clientId': settings.PLAID_CLIENT_ID,
                'secret': settings.PLAID_SECRET,
            }
        )
        api_client = plaid.ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)
    
    def _get_host(self):
        hosts = {
            'sandbox': plaid.Environment.Sandbox,
            'development': plaid.Environment.Development,
            'production': plaid.Environment.Production
        }
        return hosts.get(settings.PLAID_ENV, plaid.Environment.Sandbox)
    
    async def create_link_token(self, user_id: str, access_token: str = None) -> str:
        """Create a Link token for Plaid Link initialization."""
        request = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(client_user_id=user_id),
            client_name=settings.APP_NAME,
            products=[Products(p) for p in settings.PLAID_PRODUCTS],
            country_codes=[CountryCode(c) for c in settings.PLAID_COUNTRY_CODES],
            language='en',
            # For reconnecting items
            access_token=access_token if access_token else None
        )
        
        response = self.client.link_token_create(request)
        return response['link_token']
    
    async def exchange_public_token(self, public_token: str) -> dict:
        """Exchange a public token for an access token."""
        request = ItemPublicTokenExchangeRequest(public_token=public_token)
        response = self.client.item_public_token_exchange(request)
        
        return {
            'access_token': encrypt_sensitive_data(response['access_token']),
            'item_id': response['item_id']
        }
    
    async def get_accounts(self, encrypted_access_token: str) -> List[dict]:
        """Get all accounts for an item."""
        access_token = decrypt_sensitive_data(encrypted_access_token)
        request = AccountsGetRequest(access_token=access_token)
        response = self.client.accounts_get(request)
        
        return [{
            'account_id': acc['account_id'],
            'name': acc['name'],
            'official_name': acc['official_name'],
            'type': acc['type'],
            'subtype': acc['subtype'],
            'mask': acc['mask'],
            'current_balance': acc['balances']['current'],
            'available_balance': acc['balances']['available'],
            'limit': acc['balances'].get('limit'),
            'currency': acc['balances']['iso_currency_code']
        } for acc in response['accounts']]
    
    async def sync_transactions(
        self, 
        encrypted_access_token: str, 
        cursor: str = None
    ) -> dict:
        """Sync transactions using the Transactions Sync API."""
        access_token = decrypt_sensitive_data(encrypted_access_token)
        
        added = []
        modified = []
        removed = []
        has_more = True
        
        while has_more:
            request = TransactionsSyncRequest(
                access_token=access_token,
                cursor=cursor
            )
            response = self.client.transactions_sync(request)
            
            added.extend(response['added'])
            modified.extend(response['modified'])
            removed.extend(response['removed'])
            
            has_more = response['has_more']
            cursor = response['next_cursor']
        
        return {
            'added': self._transform_transactions(added),
            'modified': self._transform_transactions(modified),
            'removed': [t['transaction_id'] for t in removed],
            'cursor': cursor
        }
    
    def _transform_transactions(self, transactions: List[dict]) -> List[dict]:
        """Transform Plaid transactions to our format."""
        return [{
            'plaid_transaction_id': t['transaction_id'],
            'account_id': t['account_id'],
            'amount': t['amount'],  # Plaid: positive = outflow
            'date': t['date'],
            'datetime': t.get('datetime'),
            'name': t['name'],
            'merchant_name': t.get('merchant_name'),
            'category': t.get('personal_finance_category', {}).get('primary'),
            'subcategory': t.get('personal_finance_category', {}).get('detailed'),
            'pending': t['pending'],
            'payment_channel': t.get('payment_channel'),
            'location': {
                'city': t.get('location', {}).get('city'),
                'region': t.get('location', {}).get('region'),
                'country': t.get('location', {}).get('country'),
            } if t.get('location') else None
        } for t in transactions]
```

### 1.12 AI Insight Engine (app/ai_engine/insight_engine.py)

```python
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
import json

from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from app.config import get_settings
from app.ai_engine.prompts.system_prompts import COACH_SYSTEM_PROMPT
from app.ai_engine.prompts.few_shot_examples import INSIGHT_EXAMPLES
from app.models.insight import Insight, InsightType

settings = get_settings()

class InsightEngine:
    def __init__(self):
        if settings.AI_MODEL.startswith("gpt"):
            self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.AI_MODEL
        else:
            self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.model = settings.AI_MODEL
    
    async def generate_daily_insights(
        self,
        user_id: UUID,
        context: dict
    ) -> List[Insight]:
        """Generate 1-2 personalized daily insights."""
        
        # Build context for AI
        prompt = self._build_insight_prompt(context)
        
        # Generate insights
        if isinstance(self.client, AsyncOpenAI):
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": COACH_SYSTEM_PROMPT},
                    *INSIGHT_EXAMPLES,
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
        else:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=500,
                system=COACH_SYSTEM_PROMPT,
                messages=[
                    *INSIGHT_EXAMPLES,
                    {"role": "user", "content": prompt}
                ]
            )
            result = json.loads(response.content[0].text)
        
        return self._parse_insights(result, user_id)
    
    def _build_insight_prompt(self, context: dict) -> str:
        """Build the prompt with user context."""
        return f"""
Analyze this user's financial data and generate 1-2 helpful insights:

**Spending Summary (Last 30 Days):**
- Total Spending: ${context['total_spending']:.2f}
- By Category:
{self._format_category_spending(context['category_spending'])}

**Budget Status:**
{self._format_budget_status(context['budget_status'])}

**Goals:**
{self._format_goals(context['goals'])}

**Recent Transactions (Last 7 Days):**
{self._format_recent_transactions(context['recent_transactions'])}

**User Preferences:**
- Coaching Tone: {context['preferences']['coaching_tone']}
- Focus Areas: {', '.join(context['preferences']['focus_areas'])}

Generate insights as JSON:
{{
    "insights": [
        {{
            "type": "SAVINGS_OPPORTUNITY|SPENDING_ALERT|GOAL_PROGRESS|CELEBRATION",
            "title": "Brief title (max 50 chars)",
            "message": "Detailed insight message (max 200 chars)",
            "priority": "low|normal|high",
            "action_type": "optional action identifier",
            "data": {{optional supporting data}}
        }}
    ]
}}
"""
    
    def _format_category_spending(self, categories: dict) -> str:
        return "\n".join([
            f"  - {cat}: ${amt:.2f}" 
            for cat, amt in sorted(categories.items(), key=lambda x: -x[1])[:5]
        ])
    
    def _format_budget_status(self, budgets: List[dict]) -> str:
        if not budgets:
            return "  No budgets set"
        return "\n".join([
            f"  - {b['category']}: ${b['spent']:.2f} / ${b['budget']:.2f} ({b['percent_used']:.0f}%)"
            for b in budgets
        ])
    
    def _format_goals(self, goals: List[dict]) -> str:
        if not goals:
            return "  No active goals"
        return "\n".join([
            f"  - {g['name']}: ${g['current']:.2f} / ${g['target']:.2f} ({g['progress']:.0f}%)"
            for g in goals
        ])
    
    def _format_recent_transactions(self, transactions: List[dict]) -> str:
        return "\n".join([
            f"  - {t['date']}: {t['merchant']} - ${t['amount']:.2f} ({t['category']})"
            for t in transactions[:10]
        ])
    
    def _parse_insights(self, result: dict, user_id: UUID) -> List[Insight]:
        """Parse AI response into Insight objects."""
        insights = []
        for i in result.get('insights', []):
            insights.append(Insight(
                user_id=user_id,
                insight_type=InsightType(i['type'].lower()),
                title=i['title'][:100],
                message=i['message'][:500],
                priority=i.get('priority', 'normal'),
                action_type=i.get('action_type'),
                data=i.get('data', {}),
                expires_at=datetime.utcnow() + timedelta(days=7)
            ))
        return insights
```

### 1.13 System Prompts (app/ai_engine/prompts/system_prompts.py)

```python
COACH_SYSTEM_PROMPT = """You are a supportive, knowledgeable AI financial coach helping users improve their financial health. 

Your personality:
- Encouraging and positive, never judgmental
- Specific and actionable, using real numbers
- Concise - keep messages under 200 characters
- Varied tone - mix encouragement, gentle warnings, and celebrations
- Honest - acknowledge limitations when data is insufficient

Your rules:
1. NEVER shame users for spending choices
2. ALWAYS include specific dollar amounts and percentages
3. ALWAYS suggest a concrete next action
4. ONLY generate insights when there's genuinely useful information
5. Vary insight types - don't always focus on warnings
6. Reference user's specific goals when relevant
7. Celebrate wins, even small ones

Insight types you can generate:
- SAVINGS_OPPORTUNITY: Areas where user could reduce spending
- SPENDING_ALERT: Unusual or high spending warnings
- GOAL_PROGRESS: Updates on financial goals
- CELEBRATION: Positive financial behavior recognition

Output JSON format only, no additional text."""

CATEGORIZATION_PROMPT = """You are a financial transaction categorizer. Given a transaction name and amount, determine the most appropriate category.

Categories:
- Housing: rent, mortgage, utilities, maintenance
- Transportation: gas, public transit, rideshare, parking, auto insurance
- Food & Dining: groceries, restaurants, coffee, fast food
- Shopping: clothing, electronics, home goods
- Entertainment: streaming, gaming, events
- Health & Fitness: medical, pharmacy, gym
- Travel: flights, hotels, vacation
- Financial: bank fees, interest, investments
- Education: tuition, books, courses
- Subscriptions: software, memberships
- Income: salary, freelance, refunds (negative amounts)
- Gifts & Donations: charity, presents
- Miscellaneous: anything else

Respond with just the category name."""

GOAL_SUGGESTION_PROMPT = """You are a financial goal advisor. Based on the user's spending patterns and current financial situation, suggest specific ways they can reach their goal faster.

Be specific, practical, and encouraging. Suggest 3-5 actionable changes.

Format as JSON:
{
    "suggestions": [
        {
            "action": "Brief action title",
            "description": "Detailed explanation",
            "monthly_savings": estimated dollar amount,
            "difficulty": "easy|medium|hard"
        }
    ]
}"""
```

### 1.14 Anomaly Detection (app/ai_engine/anomaly_detector.py)

```python
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from app.models.transaction import Transaction

@dataclass
class AnomalyResult:
    transaction: Transaction
    anomaly_score: float
    reasons: List[str]

@dataclass
class UserPatterns:
    category_avg: dict[str, float]
    merchant_frequency: dict[str, int]
    typical_hours: tuple[int, int]
    known_merchants: set[str]

class AnomalyDetector:
    """Detects unusual transactions using Isolation Forest."""
    
    def __init__(self, contamination: float = 0.05):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
    
    def detect_anomalies(
        self,
        transactions: List[Transaction],
        patterns: UserPatterns,
        threshold: float = 0.6
    ) -> List[AnomalyResult]:
        """Detect anomalous transactions."""
        if len(transactions) < 50:
            return []  # Not enough data
        
        # Extract features
        features = self._extract_features(transactions, patterns)
        
        # Fit and predict
        scaled = self.scaler.fit_transform(features)
        predictions = self.model.fit_predict(scaled)
        scores = self.model.decision_function(scaled)
        
        # Collect anomalies
        anomalies = []
        for i, (pred, score) in enumerate(zip(predictions, scores)):
            normalized_score = (1 - score) / 2  # Convert to 0-1 range
            if pred == -1 and normalized_score >= threshold:
                anomalies.append(AnomalyResult(
                    transaction=transactions[i],
                    anomaly_score=float(normalized_score),
                    reasons=self._explain_anomaly(transactions[i], patterns)
                ))
        
        return sorted(anomalies, key=lambda x: x.anomaly_score, reverse=True)
    
    def _extract_features(
        self,
        transactions: List[Transaction],
        patterns: UserPatterns
    ) -> np.ndarray:
        """Extract ML features from transactions."""
        features = []
        
        for tx in transactions:
            category_avg = patterns.category_avg.get(str(tx.category_id), float(tx.amount))
            merchant_freq = patterns.merchant_frequency.get(tx.merchant_name or "", 0)
            
            features.append([
                float(tx.amount),
                float(tx.amount) / category_avg if category_avg > 0 else 1.0,
                tx.datetime.hour if tx.datetime else 12,
                tx.date.weekday(),
                1 if tx.date.weekday() >= 5 else 0,  # Weekend
                merchant_freq,
                len(tx.name or ""),
            ])
        
        return np.array(features)
    
    def _explain_anomaly(
        self,
        tx: Transaction,
        patterns: UserPatterns
    ) -> List[str]:
        """Generate explanations for anomaly."""
        reasons = []
        
        # Amount anomaly
        cat_avg = patterns.category_avg.get(str(tx.category_id), 0)
        if cat_avg > 0 and float(tx.amount) > cat_avg * 2:
            ratio = float(tx.amount) / cat_avg
            reasons.append(f"Amount is {ratio:.1f}x your typical spend in this category")
        
        # New merchant
        merchant = tx.merchant_name or tx.name
        if merchant not in patterns.known_merchants:
            reasons.append("First time transaction with this merchant")
        
        # Unusual timing
        if tx.datetime and patterns.typical_hours:
            hour = tx.datetime.hour
            if hour < patterns.typical_hours[0] or hour > patterns.typical_hours[1]:
                reasons.append("Transaction at unusual time of day")
        
        # Large transaction
        if float(tx.amount) > 500:
            reasons.append("Unusually large transaction amount")
        
        return reasons if reasons else ["Transaction pattern differs from your typical behavior"]
    
    def build_user_patterns(self, transactions: List[Transaction]) -> UserPatterns:
        """Build user spending patterns from historical data."""
        category_totals = {}
        category_counts = {}
        merchant_counts = {}
        hours = []
        merchants = set()
        
        for tx in transactions:
            # Category averages
            cat = str(tx.category_id)
            category_totals[cat] = category_totals.get(cat, 0) + float(tx.amount)
            category_counts[cat] = category_counts.get(cat, 0) + 1
            
            # Merchant frequency
            merchant = tx.merchant_name or tx.name
            merchant_counts[merchant] = merchant_counts.get(merchant, 0) + 1
            merchants.add(merchant)
            
            # Transaction hours
            if tx.datetime:
                hours.append(tx.datetime.hour)
        
        # Calculate averages
        category_avg = {
            cat: category_totals[cat] / category_counts[cat]
            for cat in category_totals
        }
        
        # Typical hours (5th to 95th percentile)
        typical_hours = (8, 22)  # Default
        if hours:
            typical_hours = (
                int(np.percentile(hours, 5)),
                int(np.percentile(hours, 95))
            )
        
        return UserPatterns(
            category_avg=category_avg,
            merchant_frequency=merchant_counts,
            typical_hours=typical_hours,
            known_merchants=merchants
        )
```

### 1.15 Main Application (app/main.py)

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.config import get_settings
from app.core.database import engine
from app.api.router import api_router

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("Starting Smart Financial Coach API...")
    yield
    logger.info("Shutting down...")
    await engine.dispose()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://fincoach.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred"}
    )

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION}
```

---

## 2. Frontend Implementation Guide

### 2.1 Project Setup

```bash
# Create Next.js project
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir

# Install dependencies
cd frontend
npm install @tanstack/react-query zustand axios recharts date-fns
npm install react-plaid-link @radix-ui/react-dialog @radix-ui/react-dropdown-menu
npm install class-variance-authority clsx tailwind-merge lucide-react
npm install zod react-hook-form @hookform/resolvers

# Install shadcn/ui
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card dialog dropdown-menu input toast tabs
```

### 2.2 API Client (src/lib/api-client.ts)

```typescript
import axios, { AxiosError, AxiosInstance } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiClient {
  private client: AxiosInstance;
  private refreshPromise: Promise<string> | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: `${API_URL}/api/v1`,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config;
        
        if (error.response?.status === 401 && originalRequest) {
          try {
            const newToken = await this.refreshToken();
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            return this.client(originalRequest);
          } catch {
            this.logout();
            window.location.href = '/login';
          }
        }
        
        return Promise.reject(error);
      }
    );
  }

  private async refreshToken(): Promise<string> {
    if (this.refreshPromise) {
      return this.refreshPromise;
    }

    this.refreshPromise = (async () => {
      const refreshToken = localStorage.getItem('refresh_token');
      const response = await axios.post(`${API_URL}/api/v1/auth/refresh`, {
        refresh_token: refreshToken,
      });
      
      const { access_token, refresh_token } = response.data;
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      
      this.refreshPromise = null;
      return access_token;
    })();

    return this.refreshPromise;
  }

  private logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  // Auth
  async login(email: string, password: string, mfaCode?: string) {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    
    const response = await this.client.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      params: mfaCode ? { mfa_code: mfaCode } : undefined,
    });
    
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('refresh_token', response.data.refresh_token);
    return response.data;
  }

  async register(data: { email: string; password: string; first_name?: string; last_name?: string }) {
    const response = await this.client.post('/auth/register', data);
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('refresh_token', response.data.refresh_token);
    return response.data;
  }

  // User
  async getMe() {
    return this.client.get('/users/me').then((r) => r.data);
  }

  async updatePreferences(preferences: Partial<UserPreferences>) {
    return this.client.patch('/users/me/preferences', preferences).then((r) => r.data);
  }

  // Accounts
  async getAccounts() {
    return this.client.get('/accounts').then((r) => r.data);
  }

  // Transactions
  async getTransactions(params: TransactionParams) {
    return this.client.get('/transactions', { params }).then((r) => r.data);
  }

  async updateTransaction(id: string, data: Partial<Transaction>) {
    return this.client.patch(`/transactions/${id}`, data).then((r) => r.data);
  }

  // Budgets
  async getBudgets() {
    return this.client.get('/budgets').then((r) => r.data);
  }

  async getBudgetSummary() {
    return this.client.get('/budgets/summary').then((r) => r.data);
  }

  async createBudget(data: CreateBudgetData) {
    return this.client.post('/budgets', data).then((r) => r.data);
  }

  // Goals
  async getGoals() {
    return this.client.get('/goals').then((r) => r.data);
  }

  async createGoal(data: CreateGoalData) {
    return this.client.post('/goals', data).then((r) => r.data);
  }

  async addContribution(goalId: string, amount: number) {
    return this.client.post(`/goals/${goalId}/contribute`, { amount }).then((r) => r.data);
  }

  // Subscriptions
  async getSubscriptions() {
    return this.client.get('/subscriptions').then((r) => r.data);
  }

  // Insights
  async getInsights(params?: { type?: string; is_read?: boolean }) {
    return this.client.get('/insights', { params }).then((r) => r.data);
  }

  async markInsightRead(id: string) {
    return this.client.post(`/insights/${id}/read`).then((r) => r.data);
  }

  // Analytics
  async getSpendingAnalytics(params: { start_date: string; end_date: string; group_by?: string }) {
    return this.client.get('/analytics/spending', { params }).then((r) => r.data);
  }

  async getCashFlowForecast() {
    return this.client.get('/analytics/forecast').then((r) => r.data);
  }

  // Plaid
  async createPlaidLinkToken() {
    return this.client.post('/plaid/link-token').then((r) => r.data);
  }

  async exchangePlaidToken(publicToken: string) {
    return this.client.post('/plaid/exchange-token', { public_token: publicToken }).then((r) => r.data);
  }
}

export const api = new ApiClient();
```

### 2.3 Auth Store (src/store/auth-store.ts)

```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { api } from '@/lib/api-client';

interface User {
  id: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  is_verified: boolean;
  mfa_enabled: boolean;
  onboarding_completed: boolean;
  subscription_tier: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (email: string, password: string, mfaCode?: string) => Promise<void>;
  register: (data: RegisterData) => Promise<void>;
  logout: () => void;
  fetchUser: () => Promise<void>;
  clearError: () => void;
}

interface RegisterData {
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email, password, mfaCode) => {
        set({ isLoading: true, error: null });
        try {
          await api.login(email, password, mfaCode);
          const user = await api.getMe();
          set({ user, isAuthenticated: true, isLoading: false });
        } catch (error: any) {
          set({
            error: error.response?.data?.detail || 'Login failed',
            isLoading: false,
          });
          throw error;
        }
      },

      register: async (data) => {
        set({ isLoading: true, error: null });
        try {
          await api.register(data);
          const user = await api.getMe();
          set({ user, isAuthenticated: true, isLoading: false });
        } catch (error: any) {
          set({
            error: error.response?.data?.detail || 'Registration failed',
            isLoading: false,
          });
          throw error;
        }
      },

      logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        set({ user: null, isAuthenticated: false });
      },

      fetchUser: async () => {
        const token = localStorage.getItem('access_token');
        if (!token) {
          set({ isAuthenticated: false });
          return;
        }

        set({ isLoading: true });
        try {
          const user = await api.getMe();
          set({ user, isAuthenticated: true, isLoading: false });
        } catch {
          set({ user: null, isAuthenticated: false, isLoading: false });
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ isAuthenticated: state.isAuthenticated }),
    }
  )
);
```

### 2.4 Dashboard Page (src/app/(dashboard)/dashboard/page.tsx)

```typescript
'use client';

import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api-client';
import { StatsCards } from '@/components/dashboard/stats-cards';
import { SpendingChart } from '@/components/dashboard/spending-chart';
import { RecentTransactions } from '@/components/dashboard/recent-transactions';
import { BudgetProgress } from '@/components/dashboard/budget-progress';
import { GoalProgress } from '@/components/dashboard/goal-progress';
import { InsightCard } from '@/components/dashboard/insight-card';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

export default function DashboardPage() {
  // Fetch all dashboard data in parallel
  const { data: accounts, isLoading: accountsLoading } = useQuery({
    queryKey: ['accounts'],
    queryFn: () => api.getAccounts(),
  });

  const { data: budgetSummary, isLoading: budgetLoading } = useQuery({
    queryKey: ['budget-summary'],
    queryFn: () => api.getBudgetSummary(),
  });

  const { data: goals, isLoading: goalsLoading } = useQuery({
    queryKey: ['goals'],
    queryFn: () => api.getGoals(),
  });

  const { data: insights, isLoading: insightsLoading } = useQuery({
    queryKey: ['insights', { is_read: false }],
    queryFn: () => api.getInsights({ is_read: false }),
  });

  const { data: spending } = useQuery({
    queryKey: ['spending-30d'],
    queryFn: () => {
      const end = new Date().toISOString().split('T')[0];
      const start = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
      return api.getSpendingAnalytics({ start_date: start, end_date: end, group_by: 'category' });
    },
  });

  const isLoading = accountsLoading || budgetLoading || goalsLoading || insightsLoading;

  // Calculate total balance
  const totalBalance = accounts?.reduce((sum: number, acc: any) => {
    if (acc.type === 'credit') {
      return sum - (acc.current_balance || 0);
    }
    return sum + (acc.current_balance || 0);
  }, 0) || 0;

  // Calculate this month's spending
  const monthlySpending = spending?.total || 0;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome back! Here's your financial overview.
        </p>
      </div>

      {/* AI Insights */}
      {insights?.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2">
          {insights.slice(0, 2).map((insight: any) => (
            <InsightCard key={insight.id} insight={insight} />
          ))}
        </div>
      )}

      {/* Stats Cards */}
      <StatsCards
        totalBalance={totalBalance}
        monthlySpending={monthlySpending}
        savingsRate={budgetSummary?.savings_rate || 0}
        accountsCount={accounts?.length || 0}
        isLoading={isLoading}
      />

      {/* Main Content Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Spending Chart */}
        <Card className="col-span-2">
          <CardHeader>
            <CardTitle>Spending by Category</CardTitle>
          </CardHeader>
          <CardContent>
            <SpendingChart data={spending?.by_category || []} />
          </CardContent>
        </Card>

        {/* Budget Progress */}
        <Card>
          <CardHeader>
            <CardTitle>Budget Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <BudgetProgress budgets={budgetSummary?.budgets || []} />
          </CardContent>
        </Card>

        {/* Goals */}
        <Card>
          <CardHeader>
            <CardTitle>Financial Goals</CardTitle>
          </CardHeader>
          <CardContent>
            <GoalProgress goals={goals || []} />
          </CardContent>
        </Card>

        {/* Recent Transactions */}
        <Card className="col-span-2">
          <CardHeader>
            <CardTitle>Recent Transactions</CardTitle>
          </CardHeader>
          <CardContent>
            <RecentTransactions />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
```

### 2.5 Insight Card Component (src/components/dashboard/insight-card.tsx)

```typescript
'use client';

import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api-client';
import { 
  Lightbulb, 
  TrendingDown, 
  Target, 
  PartyPopper, 
  AlertTriangle,
  X,
  ChevronRight
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface Insight {
  id: string;
  type: 'savings_opportunity' | 'spending_alert' | 'goal_progress' | 'celebration' | 'anomaly';
  title: string;
  message: string;
  priority: 'low' | 'normal' | 'high';
  action_type?: string;
  data?: Record<string, any>;
}

const insightConfig = {
  savings_opportunity: {
    icon: Lightbulb,
    color: 'text-yellow-500',
    bg: 'bg-yellow-50 dark:bg-yellow-950',
    border: 'border-yellow-200 dark:border-yellow-800',
  },
  spending_alert: {
    icon: TrendingDown,
    color: 'text-red-500',
    bg: 'bg-red-50 dark:bg-red-950',
    border: 'border-red-200 dark:border-red-800',
  },
  goal_progress: {
    icon: Target,
    color: 'text-blue-500',
    bg: 'bg-blue-50 dark:bg-blue-950',
    border: 'border-blue-200 dark:border-blue-800',
  },
  celebration: {
    icon: PartyPopper,
    color: 'text-green-500',
    bg: 'bg-green-50 dark:bg-green-950',
    border: 'border-green-200 dark:border-green-800',
  },
  anomaly: {
    icon: AlertTriangle,
    color: 'text-orange-500',
    bg: 'bg-orange-50 dark:bg-orange-950',
    border: 'border-orange-200 dark:border-orange-800',
  },
};

export function InsightCard({ insight }: { insight: Insight }) {
  const [dismissed, setDismissed] = useState(false);
  const queryClient = useQueryClient();

  const { mutate: markRead } = useMutation({
    mutationFn: () => api.markInsightRead(insight.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['insights'] });
    },
  });

  const config = insightConfig[insight.type] || insightConfig.savings_opportunity;
  const Icon = config.icon;

  if (dismissed) return null;

  return (
    <Card className={cn('relative overflow-hidden border', config.border, config.bg)}>
      <CardContent className="p-4">
        <div className="flex items-start gap-3">
          <div className={cn('rounded-full p-2', config.bg)}>
            <Icon className={cn('h-5 w-5', config.color)} />
          </div>
          
          <div className="flex-1 min-w-0">
            <h4 className="font-semibold text-sm">{insight.title}</h4>
            <p className="text-sm text-muted-foreground mt-1">{insight.message}</p>
            
            {insight.action_type && (
              <Button 
                variant="link" 
                size="sm" 
                className="px-0 mt-2"
                onClick={() => markRead()}
              >
                View Details <ChevronRight className="h-4 w-4 ml-1" />
              </Button>
            )}
          </div>

          <Button
            variant="ghost"
            size="icon"
            className="h-6 w-6"
            onClick={() => {
              setDismissed(true);
              markRead();
            }}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
```

### 2.6 Spending Chart (src/components/dashboard/spending-chart.tsx)

```typescript
'use client';

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { formatCurrency } from '@/lib/format';

interface SpendingData {
  category: string;
  amount: number;
  color: string;
}

const COLORS = [
  '#3B82F6', '#10B981', '#F59E0B', '#EC4899', '#8B5CF6',
  '#EF4444', '#06B6D4', '#84CC16', '#F97316', '#6366F1'
];

export function SpendingChart({ data }: { data: SpendingData[] }) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-muted-foreground">
        No spending data available
      </div>
    );
  }

  const chartData = data.map((item, index) => ({
    ...item,
    color: item.color || COLORS[index % COLORS.length],
  }));

  const total = chartData.reduce((sum, item) => sum + item.amount, 0);

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            paddingAngle={2}
            dataKey="amount"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            formatter={(value: number) => formatCurrency(value)}
            contentStyle={{
              backgroundColor: 'hsl(var(--background))',
              border: '1px solid hsl(var(--border))',
              borderRadius: '8px',
            }}
          />
          <Legend
            formatter={(value, entry: any) => (
              <span className="text-sm">
                {value}: {formatCurrency(entry.payload.amount)} 
                ({((entry.payload.amount / total) * 100).toFixed(0)}%)
              </span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
```

### 2.7 Plaid Link Integration (src/components/plaid/plaid-link-button.tsx)

```typescript
'use client';

import { useCallback, useEffect, useState } from 'react';
import { usePlaidLink } from 'react-plaid-link';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { api } from '@/lib/api-client';
import { Plus, Loader2 } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

export function PlaidLinkButton() {
  const [linkToken, setLinkToken] = useState<string | null>(null);
  const queryClient = useQueryClient();
  const { toast } = useToast();

  // Get link token on mount
  useEffect(() => {
    api.createPlaidLinkToken()
      .then((data) => setLinkToken(data.link_token))
      .catch(console.error);
  }, []);

  // Exchange public token mutation
  const { mutate: exchangeToken, isPending } = useMutation({
    mutationFn: (publicToken: string) => api.exchangePlaidToken(publicToken),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      toast({
        title: 'Account Connected',
        description: 'Your bank account has been successfully linked.',
      });
    },
    onError: () => {
      toast({
        title: 'Connection Failed',
        description: 'Failed to connect your bank account. Please try again.',
        variant: 'destructive',
      });
    },
  });

  const onSuccess = useCallback(
    (publicToken: string) => {
      exchangeToken(publicToken);
    },
    [exchangeToken]
  );

  const { open, ready } = usePlaidLink({
    token: linkToken,
    onSuccess,
  });

  return (
    <Button
      onClick={() => open()}
      disabled={!ready || isPending}
    >
      {isPending ? (
        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
      ) : (
        <Plus className="h-4 w-4 mr-2" />
      )}
      Connect Bank Account
    </Button>
  );
}
```

---

## 3. Celery Background Tasks

### 3.1 Task Configuration (app/tasks/__init__.py)

```python
from celery import Celery
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    'smart_fin_coach',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        'app.tasks.sync_tasks',
        'app.tasks.insight_tasks',
        'app.tasks.notification_tasks',
    ]
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    worker_prefetch_multiplier=1,
    task_acks_late=True,
)

# Scheduled tasks
celery_app.conf.beat_schedule = {
    'generate-daily-insights': {
        'task': 'app.tasks.insight_tasks.generate_all_user_insights',
        'schedule': crontab(hour=8, minute=0),  # 8 AM daily
    },
    'sync-all-accounts': {
        'task': 'app.tasks.sync_tasks.sync_all_plaid_items',
        'schedule': crontab(hour='*/4'),  # Every 4 hours
    },
    'send-bill-reminders': {
        'task': 'app.tasks.notification_tasks.send_bill_reminders',
        'schedule': crontab(hour=9, minute=0),  # 9 AM daily
    },
}
```

### 3.2 Sync Tasks (app/tasks/sync_tasks.py)

```python
from celery import shared_task
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.plaid import PlaidItem
from app.services.plaid_service import PlaidService
from app.services.sync_service import SyncService
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def sync_plaid_item(self, plaid_item_id: str):
    """Sync transactions for a single Plaid item."""
    import asyncio
    asyncio.run(_sync_plaid_item(plaid_item_id))

async def _sync_plaid_item(plaid_item_id: str):
    async with AsyncSessionLocal() as db:
        try:
            plaid_service = PlaidService()
            sync_service = SyncService(db)
            
            # Get Plaid item
            item = await db.get(PlaidItem, plaid_item_id)
            if not item:
                logger.error(f"Plaid item not found: {plaid_item_id}")
                return
            
            # Sync transactions
            result = await plaid_service.sync_transactions(
                item.plaid_access_token,
                item.sync_cursor
            )
            
            # Process results
            await sync_service.process_sync_result(item.user_id, item.id, result)
            
            # Update cursor
            item.sync_cursor = result['cursor']
            item.last_successful_sync = datetime.utcnow()
            await db.commit()
            
            logger.info(f"Synced {len(result['added'])} new transactions for item {plaid_item_id}")
            
        except Exception as e:
            logger.error(f"Sync failed for item {plaid_item_id}: {e}")
            raise

@shared_task
def sync_all_plaid_items():
    """Sync all active Plaid items."""
    import asyncio
    asyncio.run(_sync_all_plaid_items())

async def _sync_all_plaid_items():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(PlaidItem).where(PlaidItem.status == 'active')
        )
        items = result.scalars().all()
        
        for item in items:
            sync_plaid_item.delay(str(item.id))
```

---

## 4. Testing Strategy

### 4.1 Test Configuration (tests/conftest.py)

```python
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.core.security import hash_password, create_access_token

TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5432/fincoach_test"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def client(db_session) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture
async def test_user(db_session) -> User:
    user = User(
        email="test@example.com",
        password_hash=hash_password("TestPassword123!"),
        first_name="Test",
        last_name="User",
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user) -> dict:
    token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}
```

### 4.2 Example Tests (tests/integration/test_auth_endpoints.py)

```python
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

class TestAuthEndpoints:
    async def test_register_success(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/register", json={
            "email": "newuser@example.com",
            "password": "SecurePassword123!",
            "first_name": "New",
            "last_name": "User"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    async def test_register_weak_password(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/register", json={
            "email": "user@example.com",
            "password": "weak"
        })
        
        assert response.status_code == 422

    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        response = await client.post("/api/v1/auth/register", json={
            "email": test_user.email,
            "password": "SecurePassword123!"
        })
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    async def test_login_success(self, client: AsyncClient, test_user):
        response = await client.post("/api/v1/auth/login", data={
            "username": test_user.email,
            "password": "TestPassword123!"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        response = await client.post("/api/v1/auth/login", data={
            "username": test_user.email,
            "password": "WrongPassword123!"
        })
        
        assert response.status_code == 401

    async def test_protected_route_without_token(self, client: AsyncClient):
        response = await client.get("/api/v1/users/me")
        assert response.status_code == 401

    async def test_protected_route_with_token(self, client: AsyncClient, auth_headers, test_user):
        response = await client.get("/api/v1/users/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
```

---

## 5. Deployment Configuration

### 5.1 Docker Compose (docker-compose.yml)

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: fincoach
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: fincoach
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U fincoach"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://fincoach:${DB_PASSWORD}@db:5432/fincoach
      REDIS_URL: redis://redis:6379
      SECRET_KEY: ${SECRET_KEY}
      PLAID_CLIENT_ID: ${PLAID_CLIENT_ID}
      PLAID_SECRET: ${PLAID_SECRET}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: >
      sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"

  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://fincoach:${DB_PASSWORD}@db:5432/fincoach
      REDIS_URL: redis://redis:6379
      SECRET_KEY: ${SECRET_KEY}
      PLAID_CLIENT_ID: ${PLAID_CLIENT_ID}
      PLAID_SECRET: ${PLAID_SECRET}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
    depends_on:
      - backend
      - redis
    command: celery -A app.tasks worker --loglevel=info

  celery-beat:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://fincoach:${DB_PASSWORD}@db:5432/fincoach
      REDIS_URL: redis://redis:6379
    depends_on:
      - celery-worker
    command: celery -A app.tasks beat --loglevel=info

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      NEXT_PUBLIC_API_URL: http://backend:8000
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
```

### 5.2 Backend Dockerfile (backend/Dockerfile)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 6. Key Implementation Notes for AI Agent

### Critical Requirements
1. **Security First**: Always encrypt sensitive data (access tokens, PII)
2. **Error Handling**: Wrap all external API calls (Plaid, OpenAI) in try-catch with retries
3. **Rate Limiting**: Implement rate limiting on all public endpoints
4. **Validation**: Use Pydantic for all input validation
5. **Logging**: Structured JSON logging for all important operations
6. **Testing**: Minimum 80% code coverage, test all edge cases

### Code Quality Standards
- Follow PEP 8 for Python code
- Use type hints everywhere
- Document all public functions with docstrings
- Keep functions small and focused (< 50 lines)
- Use dependency injection for testability

### AI-Specific Guidelines
- Version all prompts and track in source control
- Include few-shot examples for consistent AI output
- Implement fallback responses when AI fails
- Cache AI responses where appropriate
- Monitor AI costs and implement spending limits

### Performance Targets
- API response time: < 200ms (p95)
- Transaction sync: < 30 seconds for 1000 transactions
- Insight generation: < 5 seconds per user
- Dashboard load: < 2 seconds

---

**Document Version:** 1.0  
**Created:** January 30, 2026  
**Purpose:** AI Agent Implementation Guide
